"""
Integration test for conflict UI with real conflict detector.

This test verifies the complete flow from conflict detection to UI rendering.
"""

import pytest
from unittest.mock import patch, MagicMock
from retrieval.conflict_detector import Conflict, detect_conflicts


class TestConflictUIIntegration:
    """Integration tests for conflict UI with real conflict detection."""
    
    def test_end_to_end_conflict_detection_and_display(self):
        """
        Test complete flow: detect conflicts from chunks and display UI.
        
        This test uses real conflict detection logic with mock UI components.
        """
        # Create chunks that should trigger conflict detection
        chunks = [
            {
                'content': 'Refund window is 60 days from purchase date.',
                'metadata': {
                    'source': 'Refund_Policy_v2_March2024.pdf',
                    'doc_date': '2024-03-01',
                    'doc_type': 'policy',
                    'section_title': 'Refund Policy',
                    'page_number': 5
                }
            },
            {
                'content': 'Refund window is 30 days from purchase date.',
                'metadata': {
                    'source': 'Refund_Policy_v1_Jan2023.pdf',
                    'doc_date': '2023-01-15',
                    'doc_type': 'policy',
                    'section_title': 'Refund Policy',
                    'page_number': 3
                }
            }
        ]
        
        # Detect conflicts using real conflict detector
        conflicts = detect_conflicts(chunks)
        
        # Verify conflict was detected
        assert len(conflicts) == 1
        conflict = conflicts[0]
        
        # Verify winner is the most recent
        assert conflict.winner['metadata']['doc_date'] == '2024-03-01'
        assert len(conflict.rejected) == 1
        assert conflict.rejected[0]['metadata']['doc_date'] == '2023-01-15'
        
        # Verify diff explanation was generated
        assert conflict.diff_explanation
        assert len(conflict.diff_explanation) > 0
        
        # Now test UI rendering with the detected conflict
        with patch('streamlit.error') as mock_error, \
             patch('streamlit.button') as mock_button, \
             patch('streamlit.session_state', {}):
            
            from app import render_conflict_warning
            render_conflict_warning(conflicts)
            
            # Verify UI was rendered
            mock_error.assert_called_once()
            error_message = mock_error.call_args[0][0]
            assert 'Conflict Detected' in error_message
            assert '1 contradiction(s)' in error_message
            
            mock_button.assert_called_once()
    
    def test_no_conflict_no_ui(self):
        """Test that chunks without conflicts don't trigger UI."""
        # Create chunks that should NOT trigger conflict detection
        chunks = [
            {
                'content': 'Refund policy for electronics.',
                'metadata': {
                    'source': 'Policy.pdf',
                    'doc_date': '2024-03-01',
                    'doc_type': 'policy',
                    'section_title': 'Electronics Refund',
                    'page_number': 5
                }
            },
            {
                'content': 'Shipping policy for international orders.',
                'metadata': {
                    'source': 'Policy.pdf',
                    'doc_date': '2024-03-01',
                    'doc_type': 'policy',
                    'section_title': 'Shipping Policy',
                    'page_number': 10
                }
            }
        ]
        
        # Detect conflicts
        conflicts = detect_conflicts(chunks)
        
        # Verify no conflicts detected
        assert len(conflicts) == 0
        
        # Test UI rendering
        with patch('streamlit.error') as mock_error, \
             patch('streamlit.button') as mock_button:
            
            from app import render_conflict_warning
            render_conflict_warning(conflicts)
            
            # Verify no UI was rendered
            mock_error.assert_not_called()
            mock_button.assert_not_called()
    
    def test_cross_doc_type_conflict_display(self):
        """Test conflict detection and display for email vs PDF conflict."""
        chunks = [
            {
                'content': 'Current discount is 20% for enterprise clients.',
                'metadata': {
                    'source': 'Pricing_Policy_2024.pdf',
                    'doc_date': '2024-03-01',
                    'doc_type': 'policy',
                    'section_title': 'Enterprise Discounts',
                    'page_number': 8
                }
            },
            {
                'content': 'We offer 15% discount for enterprise clients.',
                'metadata': {
                    'source': 'email',
                    'doc_date': '2023-06-15',
                    'doc_type': 'email',
                    'sender': 'sales@company.com',
                    'subject': 'Enterprise Discounts policy',
                    'client_keyword': 'Enterprise Discounts'
                }
            }
        ]
        
        # Detect conflicts
        conflicts = detect_conflicts(chunks)
        
        # Verify cross-doc-type conflict was detected
        assert len(conflicts) == 1
        conflict = conflicts[0]
        assert conflict.conflict_type == 'cross_doc_type'
        
        # Verify winner is PDF (more recent)
        assert conflict.winner['metadata']['doc_type'] == 'policy'
        assert conflict.rejected[0]['metadata']['doc_type'] == 'email'
        
        # Test side-by-side view rendering
        with patch('streamlit.divider'), \
             patch('streamlit.subheader'), \
             patch('streamlit.markdown') as mock_markdown, \
             patch('streamlit.info'), \
             patch('streamlit.columns') as mock_columns, \
             patch('streamlit.success'), \
             patch('streamlit.warning'), \
             patch('streamlit.container'):
            
            mock_col1 = MagicMock()
            mock_col2 = MagicMock()
            mock_columns.return_value = [mock_col1, mock_col2]
            
            from app import render_side_by_side_conflict_view
            render_side_by_side_conflict_view(conflicts)
            
            # Verify both doc types are displayed
            markdown_calls = [str(call) for call in mock_markdown.call_args_list]
            markdown_text = ' '.join(markdown_calls)
            
            # Check PDF metadata
            assert 'Pricing_Policy_2024.pdf' in markdown_text
            assert 'policy' in markdown_text
            
            # Check email metadata
            assert 'email' in markdown_text
            assert 'sales@company.com' in markdown_text


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
