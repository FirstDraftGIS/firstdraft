from appfd.forms import BasemapForm, FileForm, LinkForm, TextForm, TweetForm
from django.core.files.uploadedfile import SimpleUploadedFile

def clean_tweet(POST, debug=True):
    try:
        if debug: print "starting clean_tweet with", POST
        if "text" in POST:
            form = TweetForm({"text": POST["text"]})
            if form.is_valid():
                if debug: print "form is valid"
                result = {}
                result['text'] = form.cleaned_data['text']
                return result

    except Exception as e:
        print "CAUGHT EXCEPTION in clean_tweet:", e

def clean(POST, FILES):
    try:
        print "starting clean"

        style = {}
        if "basemap" in POST:
            basemapForm = BasemapForm({"basemap": POST['basemap']})
            if basemapForm.is_valid():
                style['basemap'] = basemapForm.cleaned_data['basemap']
        print "style after cleaning:", style

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
        return {"sources": sources, "style": style}
    except Exception as e:
        print "EXCEPTION in cleaner.clean:", e
        raise e
