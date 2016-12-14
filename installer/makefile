build:
	rsync -r --exclude='installer' --exclude=".git" ../../ChassisInfoFetcher .
	rm -rf bin
	python setup.py bdist_wheel -d bin/
	mv build bin/
	mv *egg-info bin/
	rm -R ChassisInfoFetcher 
	cp bin/ChassisInfoFetcher-*.whl bin/ChassisInfoFetcher-latest-py2.py3-none-any.whl
#	rm -R py-space-platform
	
clean:
	rm -rf bin
	rm -rf build 
	rm -rf *egg-info
#	rm  -f samples/*.html
#	rm  -f samples/*.log
#	rm  -f samples/*.xml
