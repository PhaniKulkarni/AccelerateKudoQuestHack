"""This module defines the routes for the AI Quiz Generator."""


"""Step 1: Import necessary modules"""
import logging
from flask import jsonify, Blueprint, request
from agents.quiz_ai_agent import generate_questions

"""Step 2: Create a Blueprint object"""
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

quiz_ai_routes = Blueprint("quiz_ai", __name__)


"""Step 3: Defining routes"""

@quiz_ai_routes.route('/ai/quiz/<user_id>', methods=['POST'])
def get_questions():
        """
        Endpoint to get generated questions based on a topic.
        """
        topic = request.args.get('topic')
        num_questions = request.args.get('num', default=5, type=int)

        if not topic:
            return jsonify({"error": "Topic parameter is required."}), 400

        questions = generate_questions(topic, num_questions)
        return jsonify({"questions": questions})