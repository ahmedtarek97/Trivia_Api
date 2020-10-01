import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @Done: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)

  '''
  @Done: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

  '''
  @DONE: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
        categories = Category.query.order_by(Category.id).all()
        if len(categories) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'categories': {category.id: category.type for category in categories}
        })
  '''
  @DONE: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        categories = Category.query.order_by(Category.type).all()
        if len(current_questions) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'categories': {category.id: category.type for category in categories},
            'current_category': None
        })

  '''
  @DONE: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
        deleted_question = Question.query.get(question_id)
        if deleted_question is None:
          abort(404)
        deleted_question.delete()
        return jsonify({
          'success': True,
          'deleted': question_id
        })
    except:
      abort(422)

  '''
  @DONE: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route("/questions", methods=['POST'])
  def post_question():
    question = request.json.get('question')
    answer = request.json.get('answer')
    category = request.json.get('category')
    difficulty = request.json.get('difficulty')
    if not (question and answer and category and difficulty):
      abort(422)
    try:
      new_question = Question(question, answer, category, difficulty)
      new_question.insert()
      return jsonify({
                'success': True,
                'created': new_question.id,
            })
    except:
      abort(422)


  '''
  @DONE: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    search_term = request.json.get('searchTerm', '')    
    if search_term is  None:
      abort(404)
    results = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()
    return jsonify({
                'success': True,
                'questions': [question.format() for question in results],
                'total_questions': len(results),
                'currentCategory': None                
            })
            

  
  '''
  @DONE: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
  
    filtered_questions = Question.query.filter(
    Question.category == str(category_id)).all()
    if len(filtered_questions) == 0:
      abort(404)

    return jsonify({
        'success': True,
        'questions': [question.format() for question in filtered_questions],
        'total_questions': len(filtered_questions),
        'current_category': category_id
        })
    
        


  '''
  @DONE: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random question within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_quiz_questions():
    try:
      previous_questions = request.json.get('previous_questions')
      quiz_category = request.json.get('quiz_category')
      if quiz_category['type'] == 'click':
          available_questions = Question.query.filter(
          Question.id.notin_((previous_questions))).all()
      else:
          available_questions = Question.query.filter_by(
          category=quiz_category['id']).filter(Question.id.notin_((previous_questions))).all()

      new_question = available_questions[random.randrange(
                  0, len(available_questions))].format() if len(available_questions) > 0 else None

      return jsonify({
      'success': True,
      'question': new_question
    })
    except:
      abort(422)


  '''
  @DONE: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Not found"
        }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
        }), 422
  
  return app

    