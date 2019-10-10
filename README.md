# django musician
Python code is written following [PEP 8](https://www.python.org/dev/peps/pep-0008/) sytle guide and it is based on [Django framework](https://djangoproject.com).

## How do I get set up?

1. Install Python and its packet manager (pip) 
```bash
# on a Debian based environment:
apt=(
    git
    python3-pip
    python3-setuptools
)
sudo apt-get install --no-install-recommends -y ${apt[@]}

```

2. Install virtualenv (isolate app python related requirements)
```bash
sudo pip3 install virtualenv
```

3. Clone this repository
```bash
git clone https://github.pangea.org/slamora/django-musician.git
```

4. Prepare env and install requirements
```bash
cd django-musician
virtualenv env
source env/bin/activate
pip3 install -r requirements.txt
```
5. Start django devel server (check everything is ok)
```bash
python manage.py migrate
python manage.py runserver
```

6. Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

7. If everything works, follow [Django deployment instructions](https://docs.djangoproject.com/en/2.2/howto/deployment/).
