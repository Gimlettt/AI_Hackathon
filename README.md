# AI_Hackathon
 
## 1. LLM as Scorer
Input: <br>
The input includes factual information about the assigment, including the assignment name, deadline, and its descriptions. 
```
{
    Assignment_Name: "3A1",
    Deadline: "",
    Description: "(Text description about the assignment. Extracted from PDF files)"
}
```

Output: <br>
The LLM is used to quantify/evaluate the model under multiple dimensions and create a vector of scores.
```
{
    Complexity: ,
    Urgency: ,
    Time_Consumption: ,
    Mark(Weight): ,
    Importance(Risk): ,


}
```


## 2. LLM to construct user profile  memory
This LLM is used to construct the personlization element. This includes subjective information towards the assignment, e.g. difficulty, preference, etc. This should also be some assignment-specific, multidimensional score.
- When opening the application, ask user "how do you feel today?" to collect status information.


## 3. LLM to make schedule
Using the scores from both LLM outputs, make a scheduling decision. 
```
{
    Assignment: "",
    Times: [{start:"", end:""}, 
            {start:"", end:""}]
    
}
```
Note that a single assignment might be separated into a few slots. 