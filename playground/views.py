from django.http import HttpResponse
from django.shortcuts import render

def calculate():
  x = 1
  y = 2
  return x + y

def say_hello(request):
  x = calculate()
  # return HttpResponse('Hello World!')
  return render(request, 'hello.html', {'name': 'Mike'})
