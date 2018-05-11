set -e

sudo git clone https://github.com/mapnik/mapnik /mapnik --depth 1
cd /mapnik
sudo git submodule update --init
sudo bash bootstrap.sh
sudo ./configure CUSTOM_CXXFLAGS='-D_GLIBCXX_USE_CXX11_ABI=0' CXX='clang++-3.8' CC='clang-3.8' | grep -v 'yes$'
sudo make | grep -v 'clang++-3.8'
#sudo make test
sudo make install | grep -v '^Install File:'
