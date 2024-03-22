from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Book, MindSpace_Conversation, Video,get_upload_path_video
from .forms import BookSelectionForm
from chromadb_setup import to_csv, create_vector_db,response_generate , main
import os
from .prompts import choose_book_system_message,quiz_prompt,get_mindspace_input,gpt_solver, mindspace_role_prompt,youtube_system_message
from .helpers import add_message, make_openai_call,make_openai_vision_call
from .youtube_transcript import get_video_id, get_video_title, get_video_transcript
import json
import pandas as pd
import tempfile
import ast
from django.http import StreamingHttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response

from django.http import JsonResponse



# Create your views here.
def login_view(request):
    if request.method == "POST":
        aadhar = request.POST["aadhar"]
        password = request.POST["password"]
        user = authenticate(request, username=aadhar, password=password)
        
        # Check if authentication successful
        
        if user is not None:
            login(request, user)
            messages.success(request, 'You are now Logged In.')
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "api/login.html", {
                "message": "Invalid username and/or password."
            })  
    else:
        return render(request, "api/login.html")
    

def register_user(request):
    if request.method == "POST":

        #register details
        mail_id = request.POST["mail_id"]
        name = request.POST["name"]
        password = request.POST["password"]
        confirmation = request.POST["confirm_password"]
        role = request.POST["role"]
        sub_role = request.POST["sub_role"]
        
        if password != confirmation:
            return render(request,'api/register.html',{
                'message':'Passwords Must Match'
            })
        
        try:
            user = User.objects.create_user(username=mail_id, email=mail_id, password=password)
            user.first_name = name
            user.role = role
            user.sub_role = sub_role
            
            user.save()

            messages.success(request, 'New User Registered Successfully')

            login(request, user)

            return HttpResponseRedirect(reverse("index"))

        except IntegrityError:
            return render(request, "api/register.html", {
                "message": "Existing User/AADHAR."
            })

    else:
        return render(request, "api/register.html")
    
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse(login_view))


@login_required
def index(request):
    return render(request,'api/index.html')

@csrf_exempt
@login_required
def upload_video(request):
    if request.method=="POST":
        data= json.loads(request.body)
        youtube_link= data['youtube_link']

        video_id= get_video_id(youtube_link)
        video_title= get_video_title(youtube_link)
        video_transcript= get_video_transcript(video_id)
        # transcript= ast.literal_eval(video_transcript)
        print(video_transcript)
        print('1')

        video=Video()
        video.video_id= video_id
        video.video_link= youtube_link
        video.video_name= video_title
        video.user= request.user
        try:
            video.save()
            print('success')
        except:
            return render(request, 'api/upload_files.html', {'error_message': 'error'})

        print('2')
        def save_transcript_to_csv(video_id, transcript):
            try:
                df = pd.DataFrame({'video_id': [video_id]*len(transcript),
                                'Content': [x['text'] for x in transcript]})
                
                # Save DataFrame to CSV
                df.to_csv('output.csv', index=False)
                
                print(f'Transcript for video {video_id} saved successfully.')
            except Exception as e:
                print(f"Error saving transcript to CSV: {e}")
        save_transcript_to_csv(video_id, video_transcript)
        # def save_transcript_to_csv(video_id, video_transcript):
        #     try:
        #         df = pd.DataFrame({'video_id': [video_id]*len(video_transcript),
        #                         'content': [x['text'] for x in video_transcript]})
                
        #         # Save DataFrame to CSV
        #         df.to_csv('output.csv', index=False)
                
        #         print(f'Transcript for video {video_id} saved successfully.')
        #     except Exception as e:
        #         print(f"Error saving transcript to CSV: {e}")
        
        # save_transcript_to_csv(video_id, transcript)
        # with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as temp_file:
        #     temp_file.write(video_transcript)
        #     temp_file_path = temp_file.name
        #     print(temp_file_path)

            # create collection with video id
            # to_csv.convert_files_in_folder(temp_file_path)
        

            
        csv_path= 'output.csv'
        collection_manager = create_vector_db.CreateCollection(video_id)
        db_collection = collection_manager.db_collection(True, csv_path)
            
            

            # After using the temporary file, you can delete it explicitly if needed
        # os.remove(temp_file_path)
        print('3')

        return redirect('upload_files')

def delete_video(request, video_id):
    video = get_object_or_404(Video, id=video_id, user=request.user)

    # delete book from path?

    create_vector_db.CreateCollection(video.video_id).remove_collection()

    video.delete()

    return redirect('upload_files')

@login_required
def upload_files(request):
    if request.method=='POST':
        book= Book()
        book.user= request.user
        book.book_name= request.POST['fileName']
        book.book_file= request.FILES['uploaded_file']
        book.book_category= request.POST['book_category']
        
        try:
            book.save()
            print('success')
        except:
            return render(request, 'api/upload_files.html', {'error_message': 'error'})

        # print(book.book_file.path)
        to_csv.convert_files_in_folder(book.book_file.path)
        csv_path= 'output.csv'
        collection_manager = create_vector_db.CreateCollection(book.book_name)
        db_collection = collection_manager.db_collection(True, csv_path)

        user_books = Book.objects.filter(user=request.user)
        user_videos= Video.objects.filter(user= request.user)
        return render(request, 'api/upload_files.html', {
            'message': 'got file',
            'user_books': user_books,
            'user_videos':user_videos
        })
    else:
        user_books = Book.objects.filter(user=request.user)
        user_videos= Video.objects.filter(user= request.user)
        return render(request, 'api/upload_files.html',{'user_books': user_books, 'user_videos':user_videos})

def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, user=request.user)

    # delete book from path?

    create_vector_db.CreateCollection(book.book_name).remove_collection()

    book.delete()

    return redirect('upload_files')

def update_book(request,book_id):
    book = get_object_or_404(Book, id=book_id, user=request.user)

    if request.method == 'POST':
        new_category = request.POST['book_category']

        # Check if the new category is different from the current one
        if book.book_category != new_category:
            book.book_category = new_category
            book.save()

    return redirect('upload_files')

@login_required
def ask_questions(request):
    if request.method== 'POST':
        # Fetch books for the current user
        user_books = Book.objects.filter(user=request.user)
        instance_book_form = BookSelectionForm(request.POST, user_books=user_books)

        username= str(request.user)
        question_query= request.POST['question_query']

        selected_book_id = request.POST.get('selected_book')
        selected_book = Book.objects.get(id=selected_book_id)
        category=selected_book.book_category

        # now get collection name from category and book name
        # then query the question

        def run_query_gpt(category, collection, query: str) -> None:
            response = response_generate.Responce()
            # print(query)
            results = collection.query(query_texts=[query], n_results=5)
            print(results)
            results_list = results['documents'][0]
            results_page = results['ids'][0]
            result_str = [f'{i + 1}. {result_}\n' for i, result_ in enumerate(results_list)]
            results_prompt = ''.join(result_str)


            # auto choose prompt based on book category
            system_message= choose_book_system_message(category)

            gpt_prompt = f"""
            Query = {query} \n
            According to the query, I have retrieved these results:
            Results: {results_prompt}
            Page_no: {results_page}
            """

            # print("ANSWER GIVEN BY GPT: \n")
            gpt_response = response.func_responce(system_message, gpt_prompt)
            # print(gpt_response)
            return gpt_response
        # collection name= file name

        # ek time pe ek hi collection ban rhi h correct that
        relevant_collection=create_vector_db.CreateCollection(selected_book.book_name).create_collection()
        # print(relevant_collection)
        answer_by_gpt= run_query_gpt(category,relevant_collection, question_query)


        return render(request, 'api/ask_questions.html',{'user_books': user_books, 'form': instance_book_form,'answer_by_gpt':answer_by_gpt})
    else:
        # Fetch books for the current user
        user_books = Book.objects.filter(user=request.user)
        # print(user_books)
        form = BookSelectionForm(user_books=user_books)
        return render(request, 'api/ask_questions.html',{'user_books': user_books, 'form': form, })



@csrf_exempt
@login_required
def TestEval(request):
    if request.method=='POST':
        print(request.POST)
        # data= json.loads(request.body)
        questions_json = request.session.get('questions')
        for i in range(len(questions_json['questions'])):
            print(f'question_{i}')

        user_answers = [request.POST.get(f'question_{i}') for i in range(len(questions_json['questions']))]
        correct_answers = [question['correct_answer'] for question in questions_json['questions']]
        print(user_answers)
        print(correct_answers)

        user_books = Book.objects.filter(user=request.user)
        score = sum(user_answer == str(correct_answer) for user_answer, correct_answer in zip(user_answers, correct_answers))
        score_percentage = (score * 100) / len(correct_answers)

        print(score)
        return render(request, 'api/quiz_generator.html', {'score': score, 'total_questions': len(correct_answers), 'user_books':user_books})
        # return Response({'score': score, 'total_questions': len(correct_answers)})
    else:
        return redirect("quiz_generator")

def quiz_generator(request):
    if request.method=='POST':
        # del request.session['test_generated']
        user_books = Book.objects.filter(user=request.user)
        username= str(request.user)
        # test_generated= request.session.get('test_generated')

        question_query= request.POST['quiz_query']
        quiz_difficulty= request.POST['quiz_difficulty']
        remarks= request.POST['quiz_remarks']

        selected_book_id = request.POST.get('selected_book')
        selected_book = Book.objects.get(id=selected_book_id)

        category=selected_book.book_category

        def run_query_gpt(category,quiz_difficulty, collection,remarks, query: str) -> None:
            response = response_generate.Responce()
            # print(query)
            results = collection.query(query_texts=[query], n_results=10)
            # print(results)
            results_list = results['documents'][0]
            results_page = results['ids'][0]
            result_str = [f'{i + 1}. {result_}\n' for i, result_ in enumerate(results_list)]
            results_prompt = ''.join(result_str)


            # auto choose prompt based on book category
            # system_message= quiz_prompt(category, quiz_difficulty)
            format='''
            {
                questions:[
                    {
                        "question": "sample question 1?",
                        "options": {
                            "a": "sample option",
                            "b": "sample option",
                            "c": "sample option",
                            "d": "sample option"
                        },
                        "correct_answer": "a"
                    }
                    {
                        same format for all the questions as above
                    }
                ]
            }
            '''

            system_message=f'''
                You are a very smart ai, expert in {category} that can test all the aspects of a topic.
                You have to always create a test from the given topic/chapter in the query of difficulty-{quiz_difficulty}.
                Give answer in Json format.
                Dont go beyond the scope of the Results provided. Validate your knowledge with the results.
                If not provided with number or type of questions, create 10 mcq questions, else do as specified.
                The questions generated should be in the following format ONLY:
                Format: {format}
            '''
            # print(system_message)

            gpt_prompt = f"""
            Query = {query} \n
            Remarks: {remarks}
            According to the query, I have retrieved these results:
            Results: {results_prompt}
            Page_no: {results_page}
            """

            # print("ANSWER GIVEN BY GPT: \n")
            gpt_response = response.func_responce(system_message, gpt_prompt)
            print(gpt_response)
            return gpt_response
        
        relevant_collection=create_vector_db.CreateCollection(selected_book.book_name).create_collection()
        # print(relevant_collection)
        questions= run_query_gpt(category,quiz_difficulty,relevant_collection,remarks, question_query)
        # print(answer_by_gpt)
        questions_json= json.loads(questions)
        request.session['questions']= questions_json
        # test_generated= 'yes'
        # request.session['test_generated']= test_generated

        return render(request, 'api/quiz_generator.html',{'user_books':user_books, 'answer_by_gpt':questions_json})
    else:
        # Fetch books for the current user
        user_books = Book.objects.filter(user=request.user)
        # print(user_books)
        # form = BookSelectionForm()
        return render(request, 'api/quiz_generator.html',{'user_books': user_books})



def learn_help_html(request):
    # Fetch books for the current user
    user_books = Book.objects.filter(user=request.user)
    # user_books = Book.objects.filter(user=1)
    return render(request, 'api/learn_help.html',{'user_books': user_books})

def get_response(messages,stream:bool=True):
        if stream:
            for result in make_openai_call(messages=messages,stream=stream):
                yield result

@login_required
@csrf_exempt
def LearnHelp(request):
    if request.method=='POST':
        data = json.loads(request.body)
        selected_book_id= data['selected_book']
        question_query= data['question_query']
        print(selected_book_id, question_query)
        selected_book = Book.objects.get(id=selected_book_id)
        category=selected_book.book_category

        system_message=choose_book_system_message(category)

        message=[{
            'role':"system",
            'content':system_message
        }]
        user_question = get_mindspace_input(question_query)

        def run_query_gpt(category, collection, query: str) -> None:
            response = response_generate.Responce()
            # print(query)
            results = collection.query(query_texts=[query], n_results=5)
            print(results)
            results_list = results['documents'][0]
            results_page = results['ids'][0]
            result_str = [f'{i + 1}. {result_}\n' for i, result_ in enumerate(results_list)]
            results_prompt = ''.join(result_str)


            # auto choose prompt based on book category
            # system_message= choose_book_system_message(category)

            gpt_prompt = f"""
            Query = {query} \n
            According to the query, I have retrieved these results:
            Results: {results_prompt}
            Page_no: {results_page}
            """

            return gpt_prompt

        relevant_collection=create_vector_db.CreateCollection(selected_book.book_name).create_collection()
        
        user_role= user_question+run_query_gpt(category,relevant_collection, question_query)
        add_message('user',user_role,messages=message)

        # Create a StreamingHttpResponse with a generator function
        return StreamingHttpResponse(get_response(messages=message), content_type='text/event-stream')

@login_required
@csrf_exempt
def LoadBook(request):
    if request.method=='POST':
        data= json.loads(request.body)
        selected_book_id= data['selected_book']
        selected_book = Book.objects.get(id=selected_book_id)
        filename= selected_book.book_name
        path_final="/media/"+str(selected_book.book_file)


        return JsonResponse({'upload_path':path_final})

@login_required
@csrf_exempt
def YoutubeAi(request):
    data= json.loads(request.body)
    selected_video_id= data['selected_video']
    question_query= data['question_query']
    selected_video= Video.objects.get(id=selected_video_id)
    video_id= selected_video.video_id

    system_message= youtube_system_message()
    # print(system_message)
    message=[{
        'role':"system",
        'content':system_message
    }]

    user_question = get_mindspace_input(question_query)

    def run_query_gpt(collection, query: str) -> None:
        response = response_generate.Responce()
        # print(query)
        results = collection.query(query_texts=[query], n_results=50)
        # print(results)
        results_list = results['documents'][0]
        results_page = results['ids'][0]
        result_str = [f'{i + 1}. {result_}\n' for i, result_ in enumerate(results_list)]
        results_prompt = ''.join(result_str)


        gpt_prompt = f"""
        Query = {query} \n
        According to the query, I have retrieved these results:
        Results: {results_prompt}
        Page_no: {results_page}
        """

        return gpt_prompt

    relevant_collection=create_vector_db.CreateCollection(video_id).create_collection()
    print(relevant_collection)
    
    user_role= user_question+run_query_gpt(relevant_collection, question_query)
    add_message('user',user_role,messages=message)

    
    
    return StreamingHttpResponse(get_response(messages=message), content_type='text/event-stream')



def youtube_ai_html(request):
    user_videos= Video.objects.filter(user=request.user)

    return render(request, 'api/youtube_ai_html.html',{'user_videos': user_videos})

@login_required
@csrf_exempt
def LoadVideo(request):
    if request.method=='POST':
        data= json.loads(request.body)
        selected_video_id= data['selected_video']
        selected_video= Video.objects.get(id=selected_video_id)
        video_id= selected_video.video_id
        return JsonResponse({'video_id':video_id})

def mindspace_html(request):
    return render(request,"api/mindspace.html")

@login_required
@csrf_exempt
def Mindspace(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_query = data['user_query']

        previous_chat = MindSpace_Conversation.objects.all()
        message = [{
                'role':"system",
                'content':f"""{mindspace_role_prompt}"""
            }]
        if previous_chat != None:
            for prev in previous_chat:
                add_message('user',str(prev.user_query),messages=message)

        # messages = message + mindspace_messages(user_query=user_query)
        user_role = get_mindspace_input(user_query)
        add_message('user',user_role,messages=message)

        obj = MindSpace_Conversation()
        obj.user_query = user_query
        obj.save()
        
        # Create a StreamingHttpResponse with a generator function
        return StreamingHttpResponse(get_response(messages=message), content_type='text/event-stream')
        



from .models import Image_conversation
@csrf_exempt
@login_required
def Vision(request):
    if request.method == 'POST' and request.FILES.get('image'):
        if request.FILES.get('image') is not None:
            image_file = request.FILES.get('image')

            result = make_openai_vision_call(image_path=image_file)

            return JsonResponse({'vision_response':result})

        
@csrf_exempt
@login_required
def Vision_Stream(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        metadata = data['metadata']

        print(request.user)

        print(request.user)

        messages = []
        add_message('system','You just got data from an image . Use all the provided data and create a brief summary of what the data in image was.',messages)
        add_message('user',f""" METADATA : {metadata}""",messages=messages)

        return StreamingHttpResponse(get_response(messages=messages), content_type='text/event-stream')
        

@csrf_exempt
@login_required
def Solve_Question(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_query = data['user_query']
        # print(user_query)

        metadata = data['metadata']
        # print(metadata)

        category = data['category']
        


        context = gpt_solver(metadata=metadata,category=category)

        # print(context)
        messages = []
        add_message("system",context,messages=messages)

        add_message("user",user_query,messages=messages)

        
        return StreamingHttpResponse(get_response(messages=messages), content_type='text/event-stream')

def vision_html(request):
    return render(request,'api/vision.html')

# vision: maths question me approach bta de , baaki me solve krde etc , css , prompt improve for student
# midspace: entry pe line to define , dark mode, image icon mindpace
# voice output for reponse 
# quiz generator prompt improve
# index page setup with cards