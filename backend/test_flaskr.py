import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from models import setup_db, Question, Category
from flaskr import create_app


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('postgres@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Question.query.count(), data['total_questions'])
        self.assertTrue(data['questions'])

    def test_delete_question(self):
        """Test _____________ """
        last_id = Question.query.order_by(Question.id.desc()).first().id
        res = self.client().delete('/questions/{0}'.format(last_id))
        data = json.loads(res.data)
        question = Question.query.get(last_id)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question_id'], last_id)
        self.assertEqual(question, None)

    def test_create_question(self):
        """Test _____________ """
        res = self.client().post('/questions/create',
                                 json={'question': "test new question", "answer": "created",
                                       "category": 2, "difficulty": 4})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question_id'])

    def test_question_search(self):
        """Test _____________ """
        res = self.client().post('/questions/search', json={'searchTerm': "test"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_categories_by_id(self):
        """Test _____________ """
        first_id = Category.query.first().id
        res = self.client().get('/categories/{0}'.format(first_id))
        data = json.loads(res.data)
        category = Category.query.get(first_id)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertEqual(data['current_category'], category.format())
        self.assertEqual(data['total_questions'], len(category.question_id))

    def test_quiz(self):
        """Test _____________ """
        res = self.client().post('/quiz', json={'previous_questions': [], 'quiz_category': {'type': 'click', 'id': 0}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

    def test_404_request(self):
        """Test _____________ """
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Not found')

    def test_422_request(self):
        """Test _____________ """
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], 'Un processable')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
