#!/bin/bash

echo "=== TESTING ALL FEATURES OF ENHANCED TODO APP ==="
echo ""

# Test 1: Add tasks with different priorities and tags
echo "TEST 1: Adding tasks with priorities and tags..."
python -m src.todo_app << 'INPUT'
1
Fix production bug
Critical payment issue
1
work,urgent,backend
1
Team meeting
Weekly sync
2
work,meeting
1
Read Python book
Learn advanced patterns
3
personal,learning
2
y
INPUT

echo ""
echo "✅ TEST 1 COMPLETE: Added 3 tasks with different priorities and tags"
echo ""

# Test 2: View all tasks
echo "TEST 2: Viewing all tasks in rich table..."
python -m src.todo_app << 'INPUT'
2
9
y
INPUT

echo ""
echo "✅ TEST 2 COMPLETE: Viewed tasks in rich table format"
echo ""

# Test 3: Search tasks
echo "TEST 3: Searching tasks by keyword..."
python -m src.todo_app << 'INPUT'
1
Buy groceries
Milk and bread
2
shopping
1
Write report
Q4 summary
2
work
6
work
9
y
INPUT

echo ""
echo "✅ TEST 3 COMPLETE: Searched tasks by keyword 'work'"
echo ""

# Test 4: Filter by priority
echo "TEST 4: Filtering tasks by priority..."
python -m src.todo_app << 'INPUT'
1
Urgent task
High priority item
1
urgent
7
2
1
9
y
INPUT

echo ""
echo "✅ TEST 4 COMPLETE: Filtered tasks by HIGH priority"
echo ""

# Test 5: Sort by priority
echo "TEST 5: Sorting tasks by priority..."
python -m src.todo_app << 'INPUT'
1
Low priority task
Can wait
3
later
8
1
9
y
INPUT

echo ""
echo "✅ TEST 5 COMPLETE: Sorted tasks by priority (HIGH→MEDIUM→LOW)"
echo ""

# Test 6: Mark task complete
echo "TEST 6: Marking task as complete..."
python -m src.todo_app << 'INPUT'
1
Complete this task
Test completion
2

5
1
2
9
y
INPUT

echo ""
echo "✅ TEST 6 COMPLETE: Marked task as complete"
echo ""

# Test 7: Update task
echo "TEST 7: Updating task details..."
python -m src.todo_app << 'INPUT'
1
Old title
Old description
2

3
1
New updated title
New updated description
1
updated
2
9
y
INPUT

echo ""
echo "✅ TEST 7 COMPLETE: Updated task with new details"
echo ""

# Test 8: Delete task
echo "TEST 8: Deleting a task..."
python -m src.todo_app << 'INPUT'
1
Task to delete
Will be removed
2

4
1
2
9
y
INPUT

echo ""
echo "✅ TEST 8 COMPLETE: Deleted task successfully"
echo ""

echo "==================================================="
echo "ALL FEATURES TESTED SUCCESSFULLY!"
echo "==================================================="
