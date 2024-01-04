import unittest
import os
import json  # Dodaj import modułu json
from app import app, download_audio, transcribe_audio, save_transcription_to_file

class TestAudioTranscription(unittest.TestCase):
    def setUp(self):
        # Arrange (Przygotowanie warunków początkowych)
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.test_url = "https://www.youtube.com/shorts/kpG7I2MOcnI"
        self.test_file_path = download_audio(self.test_url)

    def tearDown(self):
        # Arrange (Przygotowanie warunków końcowych)
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    def test_download_audio(self):
        # Act (Wywołanie testowanej metody)
        result = download_audio(self.test_url)

        # Assert (Sprawdzenie wyniku)
        self.assertTrue(os.path.exists(result))

    def test_transcribe_audio(self):
        # Arrange
        file_path = self.test_file_path

        # Act
        duration, seconds, sentences, text = transcribe_audio(file_path)

        # Assert
        self.assertIsInstance(duration, float)
        self.assertIsInstance(seconds, float)
        self.assertIsInstance(sentences, list)
        self.assertIsInstance(text, str)

    def test_save_transcription_to_file(self):
        # Arrange
        text_to_save = "Test transcription."

        # Act
        name = save_transcription_to_file(self.test_file_path, text_to_save)

        # Assert
        self.assertTrue(os.path.exists(name))

    def test_index_page_rendering(self):
        # Act
        response = self.app.get('/')

        # Assert
        self.assertEqual(response.status_code, 200)

    def test_valid_post_request_to_index_page(self):
        # Arrange
        data = dict(url=self.test_url)

        # Act
        response = self.app.post('/', data=data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Error', response.data)

    def test_index_page_invalid_post_request(self):
        # Arrange
        data = dict(invalid_key='invalid_value')

        # Act
        response = self.app.post('/', data=data)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertNotIn(b'Error', response.data)

    def test_invalid_url_post_request(self):
        # Arrange
        data = dict(url='invalid_url')

        # Act
        response = self.app.post('/', data=data)

        # Assert
        print("Response Status Code:", response.status_code)
        print("Response Data:", response.data)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid URL', response.data)

    def test_invalid_post_request_without_url(self):
        # Act
        response = self.app.post('/')

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Bad Request', response.data)



if __name__ == '__main__':
    unittest.main()