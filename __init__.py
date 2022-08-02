import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PATCH,DELTE,OPTIONS')
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        formatted_category = [category.format() for category in categories]
        flattened_category = dict(item.values() for item in formatted_category)
        return jsonify({
            'categories':flattened_category
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
        page = request.args.get('page',1,type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        selection = Question.query.order_by(Question.id).all()
        formatted_questions = [question.format() for question in selection]
        questions = formatted_questions[start:end] 
        categories = Category.query.all()
        formatted_category = [category.format() for category in categories]
        flattened_category = dict(item.values() for item in formatted_category)
        
        return jsonify({
            'questions':questions,
            'total_questions':len(Question.query.all()),
            'current_category':None,
            'categories': flattened_category
        })
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            
            if question is None:
                abort(404)
                
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            formatted_question = [question.format() for question in selection]
            
            return jsonify({
            'success':True,
            'deleted':question_id
        })
        except:
            abort(422)
        
                
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()
        
        new_question = body.get("question",None)
        new_answer = body.get("answer",None)
        new_category = body.get("category",None)
        new_difficulty = body.get("difficulty",None)
        
        try:
            if None not in (new_question,new_answer,new_category,new_difficulty):
                question=      Question(question=new_question,answer=new_answer,category=new_category,difficulty=new_difficulty)
                question.insert()

                return jsonify({
                'success':True
                })
        except:
            abort(422)
            

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions/search", methods=["POST"])
    def get_question():
        body = request.get_json()
        try:
            search_str = body.get("searchTerm", "").lower()
            if len(search_str) == 0:
                abort(404)

            selection = Question.query.order_by(Question.id).all()
            formatted_question = [question.format() for question in selection]
            result = []
            for q in formatted_question:
                if search_str in q['question']:
                    result.append(q)

            return jsonify ({
                'questions':result,
                'totalQuestions':len(result),
                'currentCategory':None
            })
        except:
            abort(400)
        
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions")
    def get_question_byCategory(category_id):
        try:
            selection = Question.query.filter(Question.category==str(category_id)).all()
            formatted_question = [question.format() for question in selection]
            categories= Category.query.filter(Category.id==(category_id))
            formatted_category = [category.format() for category in categories]
            currentcategory=formatted_category[0]['type']

            return jsonify({
                'questions':formatted_question,
                'totalQuestions':len(formatted_question),
                'currentCategory':currentcategory
            })
        except:
            abort(422)
        
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=["POST"])
    def get_quiz():
        body = request.get_json()
        try:
            previous_questions = body.get("previous_questions", [])
            quiz_category = body.get("quiz_category", "")

            if len(quiz_category) == 0:
                abort(404)

            currentcategory = quiz_category['id']
            selection = Question.query.filter(Question.category==currentcategory).all()
            formatted_question = [question.format() for question in selection]
            formatted_question=[q for q in formatted_question if q['id'] not in previous_questions]

            for item in random.sample(formatted_question,len(formatted_question)):
                result=item

                return jsonify({
                        'question':result
                    })
            return jsonify({
                'question':None
            })
        except:
            abort(422)
   
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "Resource Not found"
            }), 404
    
    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify(
                {"success": False,
                 "error": 422,
                 "message": "unprocessable"
                }), 422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
            }), 400
    
    return app
