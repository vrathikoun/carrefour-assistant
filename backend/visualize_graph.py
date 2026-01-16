import os
import sys

# Ajout du dossier courant au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.agent.graph import app_graph
except ImportError as e:
    print(f"Erreur d'import : {e}")
    print("Assurez-vous d'avoir installé les dépendances (pip install -r requirements.txt)")
    sys.exit(1)

def main():
    print("Génération de l'image du graphe...")
    try:
        # Génère le PNG (utilise l'API mermaid.ink en arrière-plan)
        png_bytes = app_graph.get_graph().draw_mermaid_png()
        
        output_path = "graph_visualization.png"
        with open(output_path, "wb") as f:
            f.write(png_bytes)
            
        print(f"✅ Image sauvegardée sous : {output_path}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération : {e}")
        print("Note : Cette fonction nécessite une connexion internet pour convertir le Mermaid en PNG.")

if __name__ == "__main__":
    main()
