# Image Upload and Analysis Service

This assignment involved building a service to upload an image and call OpenAI endpoints to identify the image's main subject.  
It then retrieves the focal-point coordinates of that subject.

I used a workflow technique called prompt chaining to first identify the main subject and then pass that result to the second prompt.
