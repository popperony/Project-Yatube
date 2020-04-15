from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm


def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {
        'page': page,
        'paginator': paginator
        })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by("-pub_date").all()
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {
        "group": group, "page": page, "paginator": paginator
        })


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        return render(request, 'new.html', {'form': form})
    form = PostForm()
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_count = Post.objects.filter(author=author).count()
    post_list = Post.objects.order_by("-pub_date").filter(author=author)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    status = None
    if request.user.is_authenticated:
        status_follow = Follow.objects.filter(user=request.user, author=author)
        if status_follow:
            status = True
        return render(request, 'profile.html', {
                'post_count': post_count,
                'page': page,
                'paginator': paginator,
                'author': author,
                'status': status
                }
            )
    return render(request, "profile.html", {
            'author': author,
            'post_count': post_count,
            'page': page,
            'paginator': paginator
            }
        )


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = Post.objects.get(id=post_id)
    post_count = Post.objects.filter(author=post.author).count()
    items = Comment.objects.order_by("-created").filter(post=post_id)
    form = CommentForm()
    return render(request, "post.html", {
            'author': author,
            'post_count': post_count,
            'post': post,
            'form': form,
            'items': items
            }
        )


@login_required
def post_edit(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)
    if request.user != profile:
        return redirect(
            "post",
            username=request.user.username,
            post_id=post_id
            )
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
        )
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect(
                "post",
                username=request.user.username,
                post_id=post_id
                )

    return render(
        request,
        "new.html",
        {"form": form, "post": post},
    )


def post_delete(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)
    if request.user != profile:
        return redirect(
            "post",
            username=request.user.username,
            post_id=post_id
            )
    post.delete()
    return redirect('index')

@login_required
def add_comment(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post_id = post_id
            comment.save()
            return redirect(
                "post",
                username=username,
                post_id=post_id
                )
    else:
        form = CommentForm()
    return render(
        request,
        'comments.html',
        {'form': form, 'post': post}
        )


@login_required
def follow_index(request):
    following = Follow.objects.filter(user=request.user).values('author')
    post_list = Post.objects.filter(author_id__in=following).order_by("-pub_date")
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, "follow.html",
        {'page': page, 'paginator': paginator}
        )



@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    status_follow = Follow.objects.filter(user=request.user, author=author)
    if not status_follow and author != request.user:
        follow_object = Follow.objects.create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required 
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow_object = Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', username=username)


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
