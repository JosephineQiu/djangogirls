from django.shortcuts import render, get_object_or_404
from .models import Post
from django.utils import timezone
from .forms import PostForm
from django.shortcuts import redirect
import json
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud.tone_analyzer_v3 import ToneInput
from watson_developer_cloud import LanguageTranslatorV3


language_translator = LanguageTranslatorV3(
    version='2018-05-31',
    username='apikey',
    password='365ds0s3qaRXM_FHT0qN4Aj9XlY1IBDsFjS7Y-o8jtXO')


service = ToneAnalyzerV3(
    ## url is optional, and defaults to the URL below. Use the correct URL for your region.
    url='https://gateway.watsonplatform.net/tone-analyzer/api',
    username='apikey',
    password='PxY-ZVpGwQbpCRwIgBlvOJT8lTX9pIza1d8okDDj6Nxl',
    version='2017-09-21')


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')

    for post in posts:
        posting = post.text

        translation_ch = language_translator.translate(
            text=post.text, model_id='en-zh-TW').get_result()
        translation_fr = language_translator.translate(
            text=post.text, model_id='en-fr').get_result()
        obj_ch = (json.dumps(translation_ch, indent=2, ensure_ascii=False))
        print(obj_ch)
        obj2_ch = json.loads(obj_ch)
        post.obj2_ch = obj2_ch['translations'][0]['translation']
        post.w_count_ch = obj2_ch['word_count']
        post.c_count_ch = obj2_ch['character_count']

        obj_fr = (json.dumps(translation_fr, indent=2, ensure_ascii=False))
        print(obj_fr)
        obj2_fr = json.loads(obj_fr)
        post.obj2_fr = obj2_fr['translations'][0]['translation']
        post.w_count_fr = obj2_fr['word_count']
        post.c_count_fr = obj2_fr['character_count']


        # tone_input = ToneInput(post.text)
        # post.tone = service.tone(tone_input=tone_input, content_type="application/json")
        # tone2 = str(tone)
        # post.tone3 = (tone2[1:500])
        # print(post.tone3)

        tone_input = ToneInput(post.text)
        tone = service.tone(tone_input=tone_input, content_type="application/json")
        tone_type = []
        tone_score = []
        document_tones = tone.result["document_tone"]["tones"]
        i = 0

        for i in range(len(document_tones)):
            tone_type.append(document_tones[i]["tone_name"])
            tone_score.append(document_tones[i]["score"])

        return render(request, 'blog/post_list.html', {'posts': posts,'tone_type':tone_type,'tone_score':tone_score})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})
