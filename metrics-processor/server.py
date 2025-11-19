from processor import Processor


class Server:
    def __init__(self):
        self.processor = Processor()

    def run(self):
        print("Metrics Processor Server is Listening...")

        test_string = "Hello, world! who are you?"
        response = self.processor(test_string)
        print("Response:", response)