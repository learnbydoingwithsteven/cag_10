
import json
import networkx as nx
from typing import List, Dict, Any, Tuple

from cag_engine.ollama_client import OllamaClient

class GraphEngine:
    def __init__(self, ollama_client: OllamaClient):
        self.client = ollama_client
        self.graph = nx.DiGraph()

    async def extract_knowledge(self, text: str) -> Dict[str, Any]:
        """Extract entities and relations from text using LLM."""
        prompt = f"""Extract knowledge graph triples from this text.
Text: "{text}"
Return ONLY a JSON list of objects: [{{ "subject": "Entity1", "predicate": "relation", "object": "Entity2" }}, ...]
Do not include explanation."""
        
        response, _ = await self.client.generate(prompt)
        
        try:
            # Clean response (remove markdown code blocks if any)
            clean_resp = response.replace("```json", "").replace("```", "").strip()
            triples = json.loads(clean_resp)
            self._add_triples(triples)
            return {"triples": triples, "graph_stats": self.get_stats()}
        except Exception as e:
            return {"error": str(e), "raw_response": response}

    def _add_triples(self, triples: List[Dict]):
        for t in triples:
            self.graph.add_edge(t['subject'], t['object'], relation=t['predicate'])

    def get_graph_data(self) -> Dict[str, Any]:
        """Return graph data in D3/force-graph format."""
        nodes = [{"id": n, "label": n} for n in self.graph.nodes()]
        links = [{"source": u, "target": v, "label": d.get('relation', '')} 
                 for u, v, d in self.graph.edges(data=True)]
        return {"nodes": nodes, "links": links}

    def get_stats(self):
        return {
            "num_nodes": self.graph.number_of_nodes(),
            "num_edges": self.graph.number_of_edges()
        }
