echo "setting environmental variables for pip install"
locale-gen en_US.UTF-8
export LANG=en_US.UTF-8
export LANGUAGE=en_US:en

echo "installing pip"
curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | python3

echo "upgrading pip in case version is old"
pip3 install --upgrade pip

echo "install from requirements.txt file"
pip3 install --quiet -r /firstdraft/requirements.txt

echo "install scikit-learn"
pip3 install -U scikit-learn

echo "download NLTK data"
python3 -c "import nltk; nltk.download('stopwords')"