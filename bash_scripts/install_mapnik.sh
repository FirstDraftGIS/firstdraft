# install Mapnik
# heavily based on https://github.com/mapnik/mapnik/wiki/UbuntuInstallation#ubuntu-1604

# you might have to update your outdated clang
export CXX="clang++-3.8" && export CC="clang-3.8"

# install mapnik
git clone https://github.com/mapnik/mapnik ~/mapnik-3.x --depth 10
cd ~/mapnik-3.x
git submodule update --init
source bootstrap.sh
./configure CUSTOM_CXXFLAGS="-D_GLIBCXX_USE_CXX11_ABI=0" CXX=${CXX} CC=${CC}
make
make test
sudo make install
