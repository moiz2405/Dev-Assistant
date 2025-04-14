from kokoro import KPipeline

def test_kokoro():
    try:
        pipeline = KPipeline(lang_code='en-us')
        print("Pipeline initialized successfully!")
    except Exception as e:
        print(f"Error initializing pipeline: {e}")

if __name__ == "__main__":
    test_kokoro()
