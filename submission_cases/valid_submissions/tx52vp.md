The auto grader on my assignment is looking for the result to look like

    [34,9]

instead I'm getting

    34 9

My code looks like:

    ​numbers = [34, 9, 32, 91, 58, 13, 77, 21, 56] 
    print("Numbers:", numbers)
    n = int(input("Number of elements to fetch from array: "))
    for i in range(n):
    print(numbers[i],end = " ")
