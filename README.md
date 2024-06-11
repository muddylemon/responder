# Responder

Responder is a social media automation tool designed to generate and schedule posts for World Wide Technology (WWT) across various platforms based on recent Google News articles. 

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Features

- Scrapes recent news articles from Google News for a given topic.
- Generates social media plans and posts to respond to breaking news while representing your brand.
- Supports multiple social media platforms: Twitter, Facebook, LinkedIn, and blogs.
- UI straight outta' 1997
- RAG based contextualization sourced from your own collection of documents

## Installation

To install Responder, follow these steps:

1. Clone the repository:

    ```sh
    git clone https://github.com/muddylemon/responder.git
    cd responder
    ```

2. Set up a virtual environment (optional but recommended):

    ```sh
    python -m venv venv
    source venv/bin/activate
    ```

3. Install the required dependencies:

    Consult https://pytorch.org/get-started/locally/ to get your personal pytorch installation command

    ```sh
    pip install -r requirements.txt
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121   
    ```

4. Add documents to /inputs and ingest them into the vectorstore:

    ```sh
        python ingest.py
    ```
    

## Usage

To use Responder, run the main script with a search term:

```sh
python main.py <search_term>
```

### Example

```sh
python main.py "Artificial Intelligence"
```

This will search for recent news articles about "Artificial Intelligence" and generate social media posts based on the results.

## Configuration

### Platform Instructions

Responder comes pre-configured with posting guidelines for different platforms. These instructions can be found in the `PLATFORM_INSTRUCTIONS` dictionary within the script. 

### Output Directory

The generated posts and plans are saved in the `outputs` directory by default. Results are saved as JSON files in topic based directories.

### Google News Configuration

- `NEWS_PERIOD`: The period to scrape news articles from (e.g., '30d' for 30 days).
- `NEWS_LANG`: The language of the news articles (default is 'en').
- `NEWS_REGION`: The region for the news articles (default is 'US').
- `NUM_PAGES`: The number of pages to scrape from Google News.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, feel free to open an issue or submit a pull request.

### Steps to Contribute

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a Pull Request.

