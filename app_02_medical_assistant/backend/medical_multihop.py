"""
Medical Diagnosis Assistant - Multi-hop Reasoning CAG
Uses Neo4j knowledge graph for medical reasoning
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from typing import List, Dict, Any, Tuple
from cag_engine.base import CAGTechnique
from cag_engine.ollama_client import OllamaClient
from neo4j import GraphDatabase
import json


class MedicalMultiHopCAG(CAGTechnique):
    """Multi-hop reasoning for medical diagnosis using knowledge graphs"""
    
    def __init__(self, ollama_client: OllamaClient, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        super().__init__(ollama_client)
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self._initialize_medical_knowledge()
    
    def _initialize_medical_knowledge(self):
        """Initialize medical knowledge graph with diseases, symptoms, and treatments"""
        with self.driver.session() as session:
            # Clear existing data
            session.run("MATCH (n) DETACH DELETE n")
            
            # Create diseases
            diseases = [
                {"name": "Influenza", "severity": "moderate", "category": "viral"},
                {"name": "Pneumonia", "severity": "severe", "category": "bacterial"},
                {"name": "Common Cold", "severity": "mild", "category": "viral"},
                {"name": "Bronchitis", "severity": "moderate", "category": "bacterial"},
                {"name": "COVID-19", "severity": "severe", "category": "viral"},
                {"name": "Strep Throat", "severity": "moderate", "category": "bacterial"},
                {"name": "Migraine", "severity": "moderate", "category": "neurological"},
                {"name": "Hypertension", "severity": "moderate", "category": "cardiovascular"},
            ]
            
            # Create symptoms
            symptoms = [
                {"name": "Fever", "type": "systemic"},
                {"name": "Cough", "type": "respiratory"},
                {"name": "Fatigue", "type": "systemic"},
                {"name": "Headache", "type": "neurological"},
                {"name": "Sore Throat", "type": "respiratory"},
                {"name": "Shortness of Breath", "type": "respiratory"},
                {"name": "Chest Pain", "type": "respiratory"},
                {"name": "Runny Nose", "type": "respiratory"},
                {"name": "Body Aches", "type": "systemic"},
                {"name": "Loss of Taste", "type": "sensory"},
            ]
            
            # Create treatments
            treatments = [
                {"name": "Rest and Hydration", "type": "supportive"},
                {"name": "Antibiotics", "type": "medication"},
                {"name": "Antiviral Medication", "type": "medication"},
                {"name": "Pain Relievers", "type": "medication"},
                {"name": "Cough Suppressants", "type": "medication"},
                {"name": "Oxygen Therapy", "type": "supportive"},
            ]
            
            # Create nodes
            for disease in diseases:
                session.run(
                    "CREATE (d:Disease {name: $name, severity: $severity, category: $category})",
                    **disease
                )
            
            for symptom in symptoms:
                session.run(
                    "CREATE (s:Symptom {name: $name, type: $type})",
                    **symptom
                )
            
            for treatment in treatments:
                session.run(
                    "CREATE (t:Treatment {name: $name, type: $type})",
                    **treatment
                )
            
            # Create relationships: Disease -> Symptom
            relationships = [
                ("Influenza", "Fever", 0.9),
                ("Influenza", "Cough", 0.8),
                ("Influenza", "Fatigue", 0.9),
                ("Influenza", "Body Aches", 0.8),
                ("Pneumonia", "Fever", 0.9),
                ("Pneumonia", "Cough", 0.9),
                ("Pneumonia", "Shortness of Breath", 0.8),
                ("Pneumonia", "Chest Pain", 0.7),
                ("Common Cold", "Runny Nose", 0.9),
                ("Common Cold", "Sore Throat", 0.7),
                ("Common Cold", "Cough", 0.6),
                ("COVID-19", "Fever", 0.8),
                ("COVID-19", "Cough", 0.8),
                ("COVID-19", "Loss of Taste", 0.7),
                ("COVID-19", "Fatigue", 0.9),
                ("Strep Throat", "Sore Throat", 0.9),
                ("Strep Throat", "Fever", 0.7),
                ("Migraine", "Headache", 0.95),
            ]
            
            for disease, symptom, probability in relationships:
                session.run(
                    """
                    MATCH (d:Disease {name: $disease})
                    MATCH (s:Symptom {name: $symptom})
                    CREATE (d)-[:HAS_SYMPTOM {probability: $probability}]->(s)
                    """,
                    disease=disease, symptom=symptom, probability=probability
                )
            
            # Create relationships: Disease -> Treatment
            treatment_rels = [
                ("Influenza", "Rest and Hydration"),
                ("Influenza", "Antiviral Medication"),
                ("Pneumonia", "Antibiotics"),
                ("Pneumonia", "Oxygen Therapy"),
                ("Common Cold", "Rest and Hydration"),
                ("Common Cold", "Cough Suppressants"),
                ("COVID-19", "Rest and Hydration"),
                ("COVID-19", "Oxygen Therapy"),
                ("Strep Throat", "Antibiotics"),
                ("Migraine", "Pain Relievers"),
            ]
            
            for disease, treatment in treatment_rels:
                session.run(
                    """
                    MATCH (d:Disease {name: $disease})
                    MATCH (t:Treatment {name: $treatment})
                    CREATE (d)-[:TREATED_WITH]->(t)
                    """,
                    disease=disease, treatment=treatment
                )
    
    def retrieve_context(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Extract symptoms and perform multi-hop reasoning"""
        # Step 1: Extract symptoms from query
        symptoms = self._extract_symptoms(query)
        
        # Step 2: Multi-hop reasoning through knowledge graph
        context_items = []
        
        with self.driver.session() as session:
            # Hop 1: Find diseases matching symptoms
            for symptom in symptoms:
                result = session.run(
                    """
                    MATCH (d:Disease)-[r:HAS_SYMPTOM]->(s:Symptom {name: $symptom})
                    RETURN d.name as disease, d.severity as severity, 
                           d.category as category, r.probability as probability
                    ORDER BY r.probability DESC
                    """,
                    symptom=symptom
                )
                
                for record in result:
                    context_items.append({
                        "type": "disease_symptom",
                        "symptom": symptom,
                        "disease": record["disease"],
                        "severity": record["severity"],
                        "category": record["category"],
                        "probability": record["probability"],
                        "hop": 1
                    })
            
            # Hop 2: Get all symptoms for top diseases
            top_diseases = list(set([item["disease"] for item in context_items[:3]]))
            for disease in top_diseases:
                result = session.run(
                    """
                    MATCH (d:Disease {name: $disease})-[r:HAS_SYMPTOM]->(s:Symptom)
                    RETURN s.name as symptom, s.type as type, r.probability as probability
                    ORDER BY r.probability DESC
                    """,
                    disease=disease
                )
                
                for record in result:
                    context_items.append({
                        "type": "disease_all_symptoms",
                        "disease": disease,
                        "symptom": record["symptom"],
                        "symptom_type": record["type"],
                        "probability": record["probability"],
                        "hop": 2
                    })
            
            # Hop 3: Get treatments for top diseases
            for disease in top_diseases:
                result = session.run(
                    """
                    MATCH (d:Disease {name: $disease})-[:TREATED_WITH]->(t:Treatment)
                    RETURN t.name as treatment, t.type as type
                    """,
                    disease=disease
                )
                
                for record in result:
                    context_items.append({
                        "type": "treatment",
                        "disease": disease,
                        "treatment": record["treatment"],
                        "treatment_type": record["type"],
                        "hop": 3
                    })
        
        return context_items[:top_k * 3]  # Return more items for multi-hop
    
    def _extract_symptoms(self, query: str) -> List[str]:
        """Extract symptoms from natural language query"""
        symptom_keywords = {
            "fever": "Fever",
            "cough": "Cough",
            "tired": "Fatigue",
            "fatigue": "Fatigue",
            "headache": "Headache",
            "sore throat": "Sore Throat",
            "throat": "Sore Throat",
            "breath": "Shortness of Breath",
            "breathing": "Shortness of Breath",
            "chest pain": "Chest Pain",
            "runny nose": "Runny Nose",
            "body aches": "Body Aches",
            "aches": "Body Aches",
            "taste": "Loss of Taste",
        }
        
        query_lower = query.lower()
        symptoms = []
        
        for keyword, symptom in symptom_keywords.items():
            if keyword in query_lower:
                symptoms.append(symptom)
        
        return list(set(symptoms))
    
    def augment_context(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Create multi-hop reasoning prompt"""
        # Organize context by hop
        hop1 = [c for c in context if c.get("hop") == 1]
        hop2 = [c for c in context if c.get("hop") == 2]
        hop3 = [c for c in context if c.get("hop") == 3]
        
        prompt = f"""You are a medical diagnosis assistant. Analyze the patient's symptoms using multi-hop reasoning through a medical knowledge graph.

Patient Query: {query}

REASONING PATH:

Hop 1 - Symptom to Disease Matching:
"""
        
        for item in hop1:
            prompt += f"- Symptom '{item['symptom']}' → Disease '{item['disease']}' (probability: {item['probability']:.2f}, severity: {item['severity']})\n"
        
        prompt += "\nHop 2 - Complete Disease Profiles:\n"
        
        disease_symptoms = {}
        for item in hop2:
            disease = item['disease']
            if disease not in disease_symptoms:
                disease_symptoms[disease] = []
            disease_symptoms[disease].append(f"{item['symptom']} ({item['probability']:.2f})")
        
        for disease, symptoms in disease_symptoms.items():
            prompt += f"- {disease}: {', '.join(symptoms)}\n"
        
        prompt += "\nHop 3 - Treatment Options:\n"
        
        disease_treatments = {}
        for item in hop3:
            disease = item['disease']
            if disease not in disease_treatments:
                disease_treatments[disease] = []
            disease_treatments[disease].append(item['treatment'])
        
        for disease, treatments in disease_treatments.items():
            prompt += f"- {disease}: {', '.join(treatments)}\n"
        
        prompt += """
Based on this multi-hop reasoning:
1. Identify the most likely diagnosis with confidence score
2. Explain which symptoms support this diagnosis
3. List any additional symptoms the patient should watch for
4. Recommend appropriate treatments
5. Provide important disclaimers

Remember: This is for educational purposes only. Always recommend consulting a healthcare professional.
"""
        
        return prompt
    
    def generate_response(self, augmented_prompt: str) -> Tuple[str, Dict[str, Any]]:
        """Generate diagnosis with metadata"""
        response = self.ollama_client.generate(
            prompt=augmented_prompt,
            model="llama3"
        )
        
        metadata = {
            "model": "llama3",
            "technique": "multi_hop_reasoning",
            "knowledge_source": "neo4j_medical_graph",
            "hops": 3
        }
        
        return response, metadata
    
    def process(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Process medical query with multi-hop reasoning"""
        # Retrieve context through multi-hop reasoning
        context = self.retrieve_context(query, top_k)
        
        # Augment with reasoning path
        augmented_prompt = self.augment_context(query, context)
        
        # Generate diagnosis
        response, metadata = self.generate_response(augmented_prompt)
        
        return {
            "query": query,
            "response": response,
            "context": context,
            "metadata": metadata,
            "process_steps": [
                {"step": "symptom_extraction", "description": "Extracted symptoms from query"},
                {"step": "hop1_matching", "description": "Matched symptoms to diseases"},
                {"step": "hop2_profiles", "description": "Retrieved complete disease profiles"},
                {"step": "hop3_treatments", "description": "Found treatment options"},
                {"step": "generation", "description": "Generated diagnosis with LLM"}
            ]
        }
    
    def close(self):
        """Close Neo4j connection"""
        self.driver.close()
