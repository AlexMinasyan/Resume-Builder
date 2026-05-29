# Resume Builder
This program is to allow one to more easily create and adjust their resume for various job opportunities. Say that you are eyeing a few jobs that have different specifications. Instead of having to go to Word and change your resume, export, submit, and redo this process, you can store everything that you could possibly want in a JSON file and, upon running the script, select the specific information that you want to give and have it be filled in a template. 

[Result Test 1](Testing%20Results/testing.pdf)

### How to Use
Input your information in the [json](User%20Data/dummy_info.json) file. Then simply run the python file, which gives you various specifications based on the arguments provided. Run
```
python3 testing_templates.py false dummy_info [prebuild_file]
```
Note that if you do not supply a second argument (the data file), then it will prompt for the choice. If you do not supply a first arguement (the testing argument) it will default to testing the program with the generic default from [dummy info](User%20Data/dummy_info.json) with generic specifications. If you want to supply a [prebuild_file] ([specs.json](specs.json)), then for each cateogory of object (e.g. `work`, `education`, etc.) supply a list of indices for the specific objects that you want to use. You can view the file as an example. If not, then the terminal will prompt you for the specific objects that you want. 


### How to Create a New Template
To Create a new template one simply has to layer Stacks and place objects within to display information and provide structure (Texts, Boxes, and Lines). One can create an entire resume now with around 30-40 lines of simple code. Go to the [Testing Script](testing_templates.py) to see. This gives the [result](Testing%20Results/testing_template_version.pdf) which is pratically identical to the results thus far (some of the margins are a few pixels off). One can also now add links to the objects, but this will be streamlined in the future.

One only neeed to go to the [templates](templates.py) scripts and create a new template class with parent class `Template` and give it the desired structure. Each `work`, `education`, etc. object should have its object passed into the corresponding generation function (aptly named `generate_work_object`, `generate_education_object`, etc.) so that it can be iterated over within the template. To iterate through the objects, pass a list of these generated objects into a `Stack`. 
