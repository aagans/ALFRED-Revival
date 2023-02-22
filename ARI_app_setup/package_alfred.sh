#!/bin/zsh
echo -e "Directory of App Setup Folder:"
read directory

cd $directory

python3 setup.py py2app

mv $directory/dist/ALFRED\ Revival.app $directory

unzip -o -d $directory/ALFRED\ Revival.app/Contents/Resources/lib/python3.10 $directory/ALFRED\ Revival.app/Contents/Resources/lib/python310.zip

cp /Library/Frameworks/Python.framework/Versions/3.10/lib/libcrypto.1.1.dylib $directory/ALFRED\ Revival.app/Contents/Frameworks

cp /Library/Frameworks/Python.framework/Versions/3.10/lib/libncursesw.5.dylib $directory/ALFRED\ Revival.app/Contents/Frameworks

cp /Library/Frameworks/Python.framework/Versions/3.10/lib/libssl.1.1.dylib $directory/ALFRED\ Revival.app/Contents/Frameworks

cp /Library/Frameworks/Python.framework/Versions/3.10/lib/libtcl8.6.dylib $directory/ALFRED\ Revival.app/Contents/Frameworks

cp /Library/Frameworks/Python.framework/Versions/3.10/lib/libtk8.6.dylib $directory/ALFRED\ Revival.app/Contents/Frameworks

python3 signing_addition.py

codesign -s "Developer ID Application: Aale Agans (RC7HB96RSJ)" -v --timestamp --deep --entitlements entitlements.plist --force -o runtime "ALFRED Revival.app"

ditto -c -k --keepParent "ALFRED Revival.app" "ALFREDRevival.zip"

xcrun notarytool submit 'ALFREDRevival.zip' --keychain-profile "NotaryAccount" --wait

xcrun stapler staple "ALFRED Revival.app"

rm -r build

rm -r dist

rm ALFREDRevival.zip

