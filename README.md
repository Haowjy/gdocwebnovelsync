# Gdoc Web Novel Sync

Sync your webnovel work across multiple platforms and google docs

## Notes

* Uses [google docs api](https://developers.google.com/docs/api) access google docs. Must use a Google Cloud Platform project with the API enabled (I am currently using my own API). See [https://developers.google.com/workspace/guides/create-project](https://developers.google.com/workspace/guides/create-project) for more details on how to activate your own api (google drive and google doc apis are free). Google docs scopes: [https://developers.google.com/identity/protocols/oauth2/scopes#docs](https://developers.google.com/identity/protocols/oauth2/scopes#docs)

  * After creating the OAuth 2.0, download the client secret, rename it to credentials, and put it into the secrets folder

## Supported Web Novel websites

* Scribblehub

## Set up project

### Download Python (3.8.10)

### Activate virtual env

* navigate to `gdocwebnovelsync` folder

* ```python3 -m venv venv```

* ```source env/bin/activate``` or ```.\env\Scripts\activate```

### Install all dependencies

* ```pip install -r requirements.txt```