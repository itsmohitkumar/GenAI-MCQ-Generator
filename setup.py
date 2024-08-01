from setuptools import find_packages, setup

setup(
    name='GenAI_mcqgenerator',
    version='0.0.1',
    author='Mohit Kumar',
    author_email='mohitpanghal12345@gmail.com',
    description='An AI-powered MCQ generator using Google Gemini and OpenAI GPT models',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/mcq-generator',
    install_requires=[
        'openai',
        'langchain',
        'streamlit',
        'python-dotenv',
        'PyPDF2',
        'faiss-cpu',
        'langchain-community',
    ],
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.8',
)
