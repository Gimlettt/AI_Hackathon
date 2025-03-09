# AI_Hackathon - Now What?
 

## 1. Preprocessing
Read a set of assignment description downloaded from moodle. Considering various factoring including the content and user comment, generate a comprehensive evaluation about the difficulty and importance of the assignment.

The following command does preprocessing.
```
python quantity/assignment_evaluation.py
```
- Genrates a .json file with diffiiculty, importance, etc. values for each assignment

## 2. User Mood
Asks the user about daily mood and uses this, together with the objective scores generated in step 1, to dynamically suggest three most suitable tasks to do now. 
```
python scorer.py
```

