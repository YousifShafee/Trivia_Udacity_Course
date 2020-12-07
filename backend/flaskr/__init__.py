from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random
from sqlalchemy import not_
import json
from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def paginate_question(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_question = questions[start:end]
    return current_question


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories')
    def get_categories():
        categories = Category.query.order_by('id').all()
        result = [category.format() for category in categories]
        if len(categories) == 0:
            abort(404)
        return jsonify({"categories": result})

    # Get All Questions
    @app.route('/questions')
    def get_questions():
        questions = Question.query.order_by('id').all()
        categories = Category.query.order_by('id').all()
        category = [item.format() for item in categories]
        current_question = paginate_question(request, questions)
        if len(current_question) == 0:
            abort(404)
        return jsonify(
            {"questions": current_question, 'total_questions': len(questions), 'categories': category})

    # Delete Question by ID
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_questions(question_id):
        question = Question.query.get(question_id)
        try:
            question.delete()
            return jsonify({"success": True, "question_id": question_id})
        except:
            abort(422)

    # Create Question
    @app.route('/questions/create', methods=['POST'])
    def create_questions():
        body = json.loads(request.get_data())
        qus_question = body['question']
        qus_answer = body['answer']
        qus_category = body['category']
        qus_difficulty = body['difficulty']
        try:
            question = Question(question=qus_question, answer=qus_answer, category=qus_category,
                                difficulty=qus_difficulty)
            question.insert()
            return jsonify({"success": True, "question_id": question.id})
        except:
            abort(422)

    # Search Method
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        content = request.get_json()['searchTerm']
        if content == "":
            abort(404)
        else:
            search = '%{0}%'.format(content)
            data = Question.query.filter(Question.question.ilike(search))
            questions = [question.format() for question in data]
            return jsonify({"questions": questions, "total_questions": len(questions)})

    # Get Category By ID
    @app.route('/categories/<int:category_id>')
    def get_category(category_id):
        categories = Category.query.get(category_id)
        questions = [question.format() for question in categories.question_id]
        if len(questions) == 0:
            abort(404)
        return jsonify(
            {"current_category": categories.format(), "questions": questions, "total_questions": len(questions)})

    # Get Random Question from category without repeated
    @app.route('/quiz', methods=['POST'])
    def get_quiz():
        data = request.get_json()
        # get previous_questions in list
        if data['quiz_category']['type'] == 'click':
            questions = Question.query.filter(Question.id.notin_(data['previous_questions'])).all()
        else:
            questions = Question.query.filter(Question.category == data['quiz_category']['id'], Question.id
                                              .notin_(data['previous_questions'])).all()
        if len(questions) == 0:
            abort(404)
        return jsonify({"question": random.choice(questions).format()})

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(422)
    def processable(error):
        return jsonify({
            "error": 422,
            "message": "Un processable"
        }), 422

    @app.errorhandler(500)
    def server(error):
        return jsonify({
            "error": 500,
            "message": "Internal Server Error"
        }), 500

    return app
