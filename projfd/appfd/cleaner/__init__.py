from appfd.forms import FileForm, LinkForm, TextForm
from django.core.files.uploadedfile import SimpleUploadedFile

def clean(POST, FILES):
    try:
        print "starting clean"
        sources = []
        for n in range(1000):
            key = "source_" + str(n) + "_type"
            #print 'key:', key
            #print "post:", POST 
            if key in POST:
                source_type = POST[key]
                print "source_type:", source_type
                data_key = "source_" + str(n) + "_data"
                print data_key 
                if source_type == "file":
                    if data_key in FILES:
                        print "FILES:", FILES
                        data = FILES[data_key]
                        # post data goes 
                        form = FileForm(files={"data": data})
                        if form.is_valid():
                            cleaned_data = form.cleaned_data['data']
                            if cleaned_data:
                                sources.append({"type": "file", "data": cleaned_data})
                        else:
                            print "file is not valid", form.errors
                elif source_type == "link":
                    if data_key in POST:
                        data = POST[data_key]
                        form = LinkForm({"data": data})
                        if form.is_valid():
                            cleaned_data = form.cleaned_data['data']
                            if cleaned_data:
                                sources.append({"type": "link", "data": cleaned_data.strip()})
                elif source_type == "text":
                    if data_key in POST:
                        data = POST[data_key]
                        form = TextForm({"data": data})
                        if form.is_valid():
                            cleaned_data = form.cleaned_data['data']
                            if cleaned_data:
                                sources.append({"type": "text", "data": cleaned_data.strip()})

        print "finishing clean"
        return {"sources": sources}
    except Exception as e:
        print "EXCEPTION in cleaner.clean:", e
        raise e
