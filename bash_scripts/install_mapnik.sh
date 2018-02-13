# install Mapnik
# heavily based on https://github.com/mapnik/mapnik/wiki/UbuntuInstallation#ubuntu-1604

# install mapnik
git clone https://github.com/mapnik/mapnik ~/mapnik-3.x --depth 10
cd ~/mapnik-3.x
git submodule update --init
source bootstrap.sh
./configure CUSTOM_CXXFLAGS="-D_GLIBCXX_USE_CXX11_ABI=0" CXX="clang++-3.8" CC="clang-3.8" | grep -v "yes$"
make | grep -v "clang++-3.8"
make test
make install | grep -v "^Install File:"
