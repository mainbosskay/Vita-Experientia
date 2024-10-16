# Vita Experientia "Life Experience"

## Introduction

VIta Experientia is a platform designed for individuals to share their life experiences. The project focuses on building a community where users can express their journeys, whether positive or challenging. Key backend features include secure user authentication, the ability to post life updates, and mechanisms for engaging with shared content.

### Key Features:

- API server built with FastAPI
- User authentication
- Posting and interacting with quotes
- Community engagement through comments and replies

My aim is to develop a platform that allows users to share both positive and challenging life experiences, providing support to others facing similar situations.

## How It Works

![Vita Experientia Architecture](vitaE_Backend_Project_Architecture.svg)

Vita Experientia consists of the following components:

### Applications

+ **PostgreSQL**
+ **Python3**

### APIs
+ **Google API** : Created with at least an email sending scope and the API server's root URL as one of the redirect URIs, from which the `credentials.json` and `token.json` files are generated.
+ **ImageKit.io API**: Used for CDN management. The public key, private key, and URL endpoint are saved in the `.env.local` file located in the [Project Main Directory](vitaE_Backend/)

### Environment Variables

The environment variables required for this project are stored in the `.env.local` file in `key=value` format. The table below provides details on the required variables:

| Name | Description |
|:-|:-|
| DATABASE_URL | The URL of the PostgreSQL database to connect to. |
| APP_MAX_SIGNIN | The maximum number of sign in attempts a user can make in succession. |
| IMG_PUB_KEY | Imagekit.io public key. |
| IMG_PRIV_KEY | Imagekit.io private key. |
| IMG_URL_ENDPNT | Imagekit.io url endpoint. |
| GMAIL_SENDER | The email address of the account responsible for sending emails to users. |
| APP_SECRET_KEY | The secret key for this application. |

## Installation

+ **Clone this repository by running the following command:**
```zsh
git clone https://github.com/mainbosskay/Vita-Experientia.git
```

+ **Navigate to the `vitaE_Backend` directory:**
```zsh
cd vitaE_Backend
```

+ **Create the environment variables mentioned above**

+ **Create a virtual environment:**

  #### mac0S and Linux:
    
    + Ensure that `python3` is installed on your system.
    + Run the following command to create a virtual enviroment:
    ```zsh
    python3 -m venv venv
    ```

    + Activate the virtual enviroment
    ```zsh
    source venv/bin/activate
    ```

  #### Windows:

    + Ensure that `python3` is installed on your system.
    + Run the following command to create a virtual enviroment:
    ```cmd
    python -m venv venv
    ```

    + Acitvate the virtual enviroment
    ```cmd
    venv\Scripts\activate
    ```

+ **Install the required dependencies:**
```zsh
pip3 install -r requirements.txt
```

+ **Start the PostgreSQL and Initialize the Database:**

  + Ensure `PostgreSQL` is installed on your system.
  + Run the following command to start the PostgreSQL services

| Step                                  | macOS (Homebrew)                                      | Linux                                             | Windows (Command Prompt)                              |
|:-|:-|:-|:-|
| **Start PostgreSQL service**          | ```brew services start postgresql```         | ```sudo service postgresql start```        | ```net start postgresql```                    |
| **Open interactive shell**            | ```psql postgres```                          | ```sudo -s -u postgres```                  | ```psql -U postgres```                        |
| **Initialize the database**           | ```\i db_setup/DBSetup.sql```                  | ```psql -f db_setup/DBSetup.sql```          | ```\i db_setup/DBSetup.sql```                 |
| **Exit the interactive shell**        | ```\q```                                      | ```exit```                                | ```\q```                                      |

## Usage

Run the server using
```zsh
./launch.sh
```
**NOTE:** Ensure to check the `launch.sh` script. The script is active for `zsh`, but the `bash` version is available as well.

## Demo

Watch a live demonstration of Vita Experientia [here]().


## Documentation

The `OpenAPI` documentation for the project is available in [OpenAPI.json](OpenAPI.json) and [OpenAPI.html](OpenAPI.html) formats.

## Discussion

Discuss Vita Experientia on [VE Discussions](https://github.com/mainbosskay/Vita-Experientia)

## Contributing

Contributions are welcome! Here's how you can get involved: [CONTRIBUTING](CONTRIBUTING.md)

## Author(s)

You can check out all contributor(s) to this project [Here](AUTHORS)

## Licensing

Vita Experientia is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Connect With Me

Connect with me via the following platforms [LinkedIn](https://www.linkedin.com/in/dadakehindeadeola) | [XfkaTwitter](https://x.com/kennyKayboss) | [GitHub](https://github.com/mainbosskay)
