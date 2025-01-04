from models.habit import Habit

def test_habit_creation(test_db, sample_habit_data):
    """Test creating a new habit with valid data"""
    habit = Habit.create(sample_habit_data)
    assert habit is not None
    assert habit.name == sample_habit_data['name']
    assert habit.category == sample_habit_data['category']
    assert habit.streak == 0  # Initial streak should be 0
    assert habit.reset_count == 0  # Initial reset count should be 0

def test_habit_streak_increment(test_db, sample_habit_data):
    """Test streak increment functionality"""
    habit = Habit.create(sample_habit_data)
    initial_streak = habit.streak
    
    assert habit.increment_streak()
    assert habit.streak == initial_streak + 1
    
    # Check database persistence
    updated_habit = Habit.get_by_id(habit.id)
    assert updated_habit.streak == initial_streak + 1

def test_habit_streak_reset(test_db, sample_habit_data):
    """Test streak reset functionality"""
    habit = Habit.create(sample_habit_data)
    
    # First increment streak
    habit.increment_streak()
    assert habit.streak == 1
    
    # Then reset
    assert habit.reset_streak()
    assert habit.streak == 0
    assert habit.reset_count == 1

def test_invalid_habit_creation(test_db):
    """Test creating habit with invalid data fails"""
    invalid_data = {'name': '', 'category': ''}  # Missing required fields
    habit = Habit.create(invalid_data)
    assert habit is None

def test_habit_update(test_db, sample_habit_data):
    """Test updating habit fields"""
    habit = Habit.create(sample_habit_data)
    assert habit.update({'name': 'Updated Name'})
    updated = Habit.get_by_id(habit.id)
    assert updated.name == 'Updated Name'

def test_habit_deletion(test_db, sample_habit_data):
    """Test habit deletion"""
    habit = Habit.create(sample_habit_data)
    habit_id = habit.id
    assert habit.delete()
    assert Habit.get_by_id(habit_id) is None

def test_longest_streak_update(test_db, sample_habit_data):
    """Test longest streak is updated correctly"""
    habit = Habit.create(sample_habit_data)
    
    # Build streak
    for _ in range(5):
        habit.increment_streak()
    assert habit.longest_streak == 5
    
    # Reset and build new streak
    habit.reset_streak()
    for _ in range(3):
        habit.increment_streak()
    assert habit.longest_streak == 5  # Should keep highest

def test_habit_validation(test_db):
    """Test habit data validation"""
    invalid_cases = [
        {'name': '', 'category': 'Test'},  # Empty name
        {'name': 'Test', 'repeat': 'Invalid'},  # Invalid repeat
        {'name': 'Test', 'importance': 'Medium'}  # Invalid importance
    ]
    for invalid_data in invalid_cases:
        habit = Habit.create(invalid_data)
        assert habit is None