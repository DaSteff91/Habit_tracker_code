from models.analytics import Analytics
from tests.db import DatabaseConnectorTesting
from typing import Dict, Any

class TestAnalytics:
    """Test suite for Analytics model"""

    def test_analytics_data_retrieval(self, test_db: DatabaseConnectorTesting):
        """Test analytics data retrieval"""
        # Arrange
        analytics = Analytics(test_db)      
        
        # Act
        data = analytics.get_analytics_data(test_db)
        
        # Assert
        assert isinstance(data, list)
        if data:
            assert all(isinstance(item, dict) for item in data)
            assert 'name' in data[0]
            assert 'success_rate' in data[0]

    def test_data_filtering(self, test_db: DatabaseConnectorTesting, sample_habit_data: Dict[str, Any]):
        """Test analytics data filtering"""
        # Arrange
        test_db.create_test_habit(sample_habit_data)
        analytics = Analytics(test_db)
        data = analytics.get_analytics_data(test_db)
        
        # Act
        filtered = analytics.filter_analytics_data(data, 'category', 'Health')
        
        # Assert
        assert isinstance(filtered, list)
        assert len(filtered) > 0
        assert all('category' in item for item in filtered)
        assert all('Health' in item['category'] for item in filtered)

    def test_data_sorting(self, test_db: DatabaseConnectorTesting, sample_habit_data: Dict[str, Any]):
        """Test analytics data sorting"""
        # Arrange
        test_db.create_test_habit(sample_habit_data)
        analytics = Analytics(test_db)
        data = analytics.get_analytics_data(test_db)
        
        # Act
        sorted_asc = analytics.sort_analytics_data(data, 'name', ascending=True)
        sorted_desc = analytics.sort_analytics_data(data, 'name', ascending=False)
        
        # Assert
        assert len(sorted_asc) > 0
        assert len(sorted_asc) == len(data)
        assert len(sorted_desc) == len(data)
        if len(sorted_asc) > 1:
            assert sorted_asc[0]['name'] <= sorted_asc[-1]['name']
            assert sorted_desc[0]['name'] >= sorted_desc[-1]['name']

    def test_empty_data_handling(self):
        """Test handling of empty data"""
        # Arrange
        analytics = Analytics()
        empty_data = []
        
        # Act & Assert
        assert analytics.sort_analytics_data(empty_data, 'name') == []
        assert analytics.filter_analytics_data(empty_data, 'category', 'any') == []