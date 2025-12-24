from flask import Flask, render_template, jsonify
import grpc
import os
import glossary_pb2
import glossary_pb2_grpc

app = Flask(__name__)

# Подключение к gRPC серверу (как в marketplace.py)
glossary_host = os.getenv("GLOSSARY_HOST", "localhost")
glossary_channel = grpc.insecure_channel(f"{glossary_host}:50051")
glossary_client = glossary_pb2_grpc.GlossaryServiceStub(glossary_channel)

@app.route("/")
def render_homepage():
    # Запрашиваем термины категории FUNCTIONS (аналог BookCategory.SELF_HELP)
    terms_request = glossary_pb2.TermRequest(
        category=glossary_pb2.FUNCTIONS,
        max_results=3
    )
    terms_response = glossary_client.GetTerms(terms_request)
    
    return render_template(
        "index.html",
        terms=terms_response.terms,
        category="Functions"
    )

@app.route("/api/terms")
def get_all_terms():
    terms_request = glossary_pb2.Empty()
    terms_response = glossary_client.GetAllTerms(terms_request)
    
    terms_list = []
    for term in terms_response.terms:
        terms_list.append({
            "id": term.id,
            "name": term.name,
            "definition": term.definition,
            "category": glossary_pb2.TermCategory.Name(term.category)
        })
    
    return jsonify(terms_list)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)