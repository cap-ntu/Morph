echo "Installing ffmpeg"
sudo apt-get install ffmpeg

##compile ffmpeg from the source
#sudo apt-get install build-essential libmp3lame-dev libvorbis-dev libtheora-dev libspeex-dev yasm pkg-config libfaac-dev libopenjpeg-dev libx264-dev libvpx-dev
#mkdir software
#cd software
#wget http://ffmpeg.org/releases/ffmpeg-3.4.tar.bz2
#cd ..
#mkdir src
#cd src
#tar xvjf ../software/ffmpeg-3.4.tar.bz2
#cd ffmpeg-3.4
#./configure --enable-gpl --enable-postproc --enable-swscale --enable-avfilter --enable-libmp3lame --enable-libvorbis --enable-libtheora --enable-libx264 --enable-libspeex --enable-shared --enable-pthreads --enable-libopenjpeg --enable-libfaac --enable-nonfree --enable-libvpx
#sudo make -j 2
#sudo make install
#sudo ldconfig

echo "Installation is now complete and ffmpeg (also ffprobe, ffserver, lame, and x264) should now be ready to use"

echo "Insatlling numpy"
sudo pip install numpy

echo "Installing pycurl"
sudo apt-get install python-pycurl

echo "Installing mysql"
sudo apt-get install mysql-server
sudo apt-get install mysql-client
sudo apt-get install python-dev libmysqlclient-dev

echo "Installing mysqldb"
sudo apt-get install python-mysqldb

##If dependency errors
#sudo apt-get -f install 
