# main.py
# from create_vector_db import CreateCollection
# from response import Responce

# def select_most_relevant_collection(book_name):
#     # Implement logic to select the most relevant collection based on some criteria
#     # For simplicity, let's assume there's only one collection for now
#     return CreateCollection(book_name).create_collection()

def run_query_gpt(collection, query: str) -> None:
    response = Responce()
    results = collection.query(query_texts=[query], n_results=3)
    results_list = results['documents'][0]
    results_page = results['ids'][0]
    result_str = [f'{i + 1}. {result_}\n' for i, result_ in enumerate(results_list)]
    results_prompt = ''.join(result_str)


    # CURRENTLY STATIC PROMPT HERE
    # system_message = '''
    # Explore the themes, characters, and literary devices in a book of your choice, providing insights and analysis to enhance your understanding of the author's intentions and the broader cultural or historical context. Consider how the narrative style, symbolism, and character development contribute to the overall impact of the work.
    # '''

    gpt_prompt = f"""
    Query = {query} \n
    According to the query, I have retrieved these results:
    Results: {results_prompt}
    Page_no: {results_page}
    """

    print("ANSWER GIVEN BY GPT: \n")
    gpt_response = response.func_responce(system_message, gpt_prompt)
    print(gpt_response)
    return gpt_response


# if __name__ == "__main__":
#     # Automatically select the most relevant collection
#     relevant_collection = select_most_relevant_collection()
    
#     # Example query
#     query_text = 'give me a summary of nuclear fission from this book in 500 words'
#     run_query_gpt(relevant_collection, query_text)
