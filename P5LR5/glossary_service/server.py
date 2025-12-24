from concurrent import futures
import grpc
import glossary_pb2
import glossary_pb2_grpc

# База данных терминов Python (аналог books_by_category)
terms_by_category = {
    glossary_pb2.GENERAL: [
        glossary_pb2.GlossaryTerm(id="1", name="PEP", definition="Python Enhancement Proposal", category=glossary_pb2.GENERAL),
        glossary_pb2.GlossaryTerm(id="2", name="Zen of Python", definition="Набор принципов написания кода", category=glossary_pb2.GENERAL),
    ],
    glossary_pb2.FUNCTIONS: [
        glossary_pb2.GlossaryTerm(id="3", name="Decorator", definition="Функция, модифицирующая другую функцию", category=glossary_pb2.FUNCTIONS),
        glossary_pb2.GlossaryTerm(id="4", name="Lambda", definition="Анонимная функция", category=glossary_pb2.FUNCTIONS),
    ],
    glossary_pb2.CLASSES: [
        glossary_pb2.GlossaryTerm(id="5", name="Mixin", definition="Класс, добавляющий функциональность", category=glossary_pb2.CLASSES),
        glossary_pb2.GlossaryTerm(id="6", name="Metaclass", definition="Класс, создающий классы", category=glossary_pb2.CLASSES),
    ],
}

class GlossaryServicer(glossary_pb2_grpc.GlossaryServiceServicer):
    def GetTerms(self, request, context):
        if request.category not in terms_by_category:
            context.abort(grpc.StatusCode.NOT_FOUND, "Category not found")
        
        terms_for_category = terms_by_category[request.category]
        return glossary_pb2.GlossaryResponse(terms=terms_for_category[:request.max_results])
    
    def GetAllTerms(self, request, context):
        all_terms = []
        for terms_list in terms_by_category.values():
            all_terms.extend(terms_list)
        return glossary_pb2.GlossaryResponse(terms=all_terms)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    glossary_pb2_grpc.add_GlossaryServiceServicer_to_server(GlossaryServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Glossary gRPC Server running on port 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()