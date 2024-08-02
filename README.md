# News Article Search Engine 

![Alt text](https://contenthub-static.grammarly.com/blog/wp-content/uploads/2022/08/BMD-3398.png)


## 1. Introduction to the Project
This Search Engine retrieves relevant news articles for the user-entered query from the database by computing the nearest neighbors using the ANNOY library's Approximate Nearest Neighbors algorithm. It utilizes the SBERT model to convert news article sentences into embeddings and finds the nearest neighbors using the ANNOY index. The solution is deployed on AWS using Docker, with a Flask API facilitating easy querying and retrieval.

## 2. Project Structure

```bash
NewsArticleSearchEngine
│
├── .github
│   └── workflows
│       └── automate.yml
│
├── SearchRelevancy.egg-info
│
├── artifacts
│   ├── annoy_index.ann
│   ├── article_section_mapping.pkl
│   ├── section_article_mapping.pkl
│   ├── embeddings.json
│   └── metadata.json
│   
│
├── data
│   ├── raw.csv
│   └── preprocessed.csv
│
│
│
├── notebooks
│   ├── eda.ipynb
│   └── training.ipynb
│  
│
├── src
│   ├── components
│   │   ├── data_ingestion.py
│   │   ├── data_preprocessing.py
│   │   ├── embedding_generation.py
│   │   ├── annoy_indexing.py
│   │   └── congif.py
│   │   
│   │
│   ├── exception
│   │   └── logger.py
│   │
│   ├── pipeline
│   │   ├── train_pipeline.py
│   │   └── search_pipeline.py
│   │
│   └── utils
│       └── utils.py
│
├── templates
│   ├── index.html
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── app.py
├── requirements.txt
├── requirements_dev.txt
├── setup.py
└── test.py

```
The project is organized into several components:

- `artifacts`: Contains annoy index, embeddings and meta data.
- `src`: packages the source code for data processing, embedding generation, and indexing.
- `app.py` : A simple flask application to build API for getting the search results.
- `Dockerfile` : Defines the Docker image for containerizing the flask application.
- `automate.yml` : Configures CI/CD pipelines for automated deployment.

## 3. Src Package and Training/Prediction Pipeline

The src package contains modules for data processing, embedding generation, and indexing
* **Data Ingestion**: Handles data loading .
* **Data Preprocessing**: Performs data preprocessing and splits the article into sentences or paragraphs
* **Embedding Generation**: Computes embeddings for sentences/paragraphs from articles
* **Indexing**: Builds the ANNOY index using the computed embeddings.
* **Config**: Setups the configuration of the project.

We have 2 pipelines which are 
- **Training Pipeline**: The training pipeline consists of several steps including Data ingestion, Data preprocessing, Embedding generation,  etc.. to compute and store embeddings 
- **Prediction Pipeline**: The search pipeline utilizes the annoy index model to search for the relevant news article for the user-given query.

## 4. Flask Application

The Flask application serves as the interface for interacting with the Search Engine. It provides endpoints for viewing the webpage page, testing the server's availability, and getting search results  using the ANNOY index.

### Endpoints

1. **Ping Endpoint** (`/ping`): A simple endpoint for testing the server's availability. Returns "Success" when accessed via a GET request.
2. **Search Endpoint** (`/search`): Renders the `index.html` template, which provides an interactive method to search news articles.
3. **Search API Endpoint** (`/api/search`): A simple API endpoint that accepts query and k as input and  returns the result in the form of json.

### Input Features

The Search API Endpoint (`/api/search`) endpoint accepts the following input features:

- **Query**: The search query.
- **K**: Number of relevant articles to return.

```bash
{ query: "women empowerment",
  k: 5
}
```

### Output

The (`/api/search`) endpoint endpoint returns the relevant articles from the ANNOY index.

```bash
{'query': 'your sample query',
  'results': [{'article_id': 1234,
               'category': 'business',
               'score': 0.53,
               'subcategory': 'equity - private & public',
               'title': 'We Think Balco Group (STO:BALCO) Can Stay On Top Of '
                        'Its Debt'},
              {'article_id': 13029,
               'category': 'us media',
               'score': 0.48,
               'subcategory': 'us - entrepreneur & startup',
               'title': 'Egyptian B2B trucking startup Trella secures further '
                        '$6m debt funding'}]
}
```

## 5. Dockerfile and Containerization

The Dockerfile provided in the project repository allows for containerizing the Customer Propensity Model application using a multi-stage build strategy. This strategy helps reduce the size of the final Docker image by separating the build dependencies from the runtime environment.

### Dockerfile Explanation

The Dockerfile consists of two stages:

1. **Builder Stage**: In this stage, a Python 3.8 slim-buster image is used to install the project dependencies specified in the `requirements.txt` file. This stage sets the working directory to `/install` and copies only the `requirements.txt` file to leverage Docker's caching mechanism. It then installs the dependencies into the `/install` directory using `pip`. This stage is responsible for creating a temporary image used for building the dependencies.

2. **Final Stage**: The final Docker image is created based on another Python 3.8 slim-buster image. This stage sets the working directory to `/app` and copies the installed dependencies from the builder stage into the `/usr/local` directory. It then copies the rest of the application files into the `/app` directory. After copying, any unnecessary files are cleaned up to reduce the image size. Finally, the command to run the Flask application is specified using the `CMD` directive, which starts the Flask server on `0.0.0.0:5000`.

### Building the Docker Image

To build the Docker image for the Customer Propensity Model application, navigate to the project directory containing the Dockerfile and execute the following command:

```bash
docker build -t search_engine .
```

Once the Docker image is built, you can run a Docker container using the following command:
```bash
docker run -d -p 5000:5000 search_engine
```
This command will start a Docker container based on the customer-propensity-model image, exposing port 5000 on the host machine. You can then access the Customer Propensity Model application by visiting http://localhost:5000 in your web browser


## 6. CI/CD Pipelines

The project utilizes GitHub Actions for Continuous Integration (CI) and Continuous Delivery (CD) pipelines to automate the testing, building, and deployment processes.
![1_jrdZWe4JRU5KDbWfnRxenA](https://github.com/prxdyu/customer_propensity_modelling/assets/105141574/dd8b33fe-5755-498c-83d7-24db2c807857)


### Continuous Integration (CI)

The CI pipeline ensures the correctness and reliability of the Customer Propensity Model application by running automated tests using pytest. These tests validate the functionality of key endpoints in the Flask application. The test.py file is responsible for running the tests to ensure the proper running of flask application

#### Test Workflow

- **Workflow Name**: Containerizing the Image and deploying it to EC2
- **Trigger**: Automatically triggered upon pushing changes to the `main` branch.
- **Jobs**:
  - **Job 1**: Runs tests with pytest.
  - **Job 2**: Deploys the Docker image to Amazon EC2 instance.

### Continuous Delivery (CD)

The CD pipeline automates the deployment of the Docker image containing the Flask application to an Amazon EC2 instance.

#### Workflow Steps

1. **Checkout**: Checks out the code from the repository.
2. **Install Python 3**: Sets up the Python environment for testing.
3. **Install Dependencies**: Installs project dependencies listed in `requirements_dev.txt`.
4. **Run tests with pytest**: Executes automated tests using pytest.
5. **Print AWS Secrets**: Prints AWS access keys for authentication.
6. **Configure AWS Credentials**: Configures AWS credentials for accessing services.
7. **Login to Amazon ECR**: Logs in to Amazon Elastic Container Registry (ECR) for container image storage.
8. **Build, tag, push image to Amazon ECR**: Builds the Docker image, tags it, and pushes it to Amazon ECR.
9. **Deploy docker image from ECR to EC2 instance**: Deploys the Docker image from ECR to an EC2 instance, running the Flask application.

These CI/CD pipelines ensure the application is thoroughly tested and efficiently deployed to the production environment, enhancing development productivity and maintaining application quality.



