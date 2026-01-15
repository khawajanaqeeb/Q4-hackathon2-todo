from setuptools import setup, find_packages

setup(
    name="todo-ai-chatbot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.12.0",
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "python-multipart>=0.0.6",
        "pydantic>=2.5.0",
        "sqlmodel>=0.0.16",
        "asyncio",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    author="Todo AI Team",
    author_email="todo-ai@example.com",
    description="AI-Powered Todo Chatbot for the Todo Application",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/khawajanaqeeb/Q4-hackathon2-todo",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.13",
)