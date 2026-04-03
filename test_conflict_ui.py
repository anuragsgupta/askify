"""
Unit tests for conflict warning UI components.

Tests verify:
- Warning banner visibility when conflicts detected
- Side-by-side view rendering with correct metadata
- UI hiding when no conflicts exist
- Proper display of winner vs rejected chunks
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from retrieval.conflict_detector import Conflict


class TestConflictWarningUI:
    """Test suite for conflict warning UI rendering."""
    
    def test_warning_banner_visible_when_conflicts_detected(self):
        """
        Test that warning banner is displayed when conflicts are detected.
        
        **Validates: Requirements 7.1**
        """
        # Create mock conflict
        conflict = Conflict(
            winner={
                'content': 'Refund window is 60 days',
                'metadata': {
                    'source': 'Policy_v2.pdf',
                    'doc_date': '2024-03-01',
                    'doc_type': 'policy',
                    'section_title': 'Refund Policy'
                }
            },
            rejected=[{
                'content': 'Refund window is 30 days',
                'metadata': {
                    'source': 'Policy_v1.pdf',
                    'doc_date': '2023-01-15',
                    'doc_type': 'policy',
                    'section_title': 'Refund Policy'
                }
            }],
            diff_explanation='Refund window changed from 30 to 60 days',
            conflict_type='version_update'
        )
        
        conflicts = [conflict]
        
        # Mock Streamlit components
        with patch('streamlit.error') as mock_error, \
             patch('streamlit.button') as mock_button:
            
            # Import after patching
            from app import render_conflict_warning
            
            # Call function
            render_conflict_warning(conflicts)
            
            # Verify error banner was called with conflict message
            mock_error.assert_called_once()
            call_args = mock_error.call_args[0][0]
            assert 'Conflict Detected' in call_args
            assert '1 contradiction(s)' in call_args
            
            # Verify button was displayed
            mock_button.assert_called_once()
            button_label = mock_button.call_args[0][0]
            assert 'View side-by-side' in button_label
    
    def test_warning_banner_shows_multiple_conflicts(self):
        """Test that warning banner shows correct count for multiple conflicts."""
        # Create multiple conflicts
        conflicts = [
            Conflict(
                winner={'content': 'A', 'metadata': {'source': 'doc1', 'doc_date': '2024-01-01', 'doc_type': 'policy'}},
                rejected=[{'content': 'B', 'metadata': {'source': 'doc2', 'doc_date': '2023-01-01', 'doc_type': 'policy'}}],
                diff_explanation='Change 1',
                conflict_type='version_update'
            ),
            Conflict(
                winner={'content': 'C', 'metadata': {'source': 'doc3', 'doc_date': '2024-02-01', 'doc_type': 'policy'}},
                rejected=[{'content': 'D', 'metadata': {'source': 'doc4', 'doc_date': '2023-02-01', 'doc_type': 'policy'}}],
                diff_explanation='Change 2',
                conflict_type='policy_change'
            )
        ]
        
        with patch('streamlit.error') as mock_error, \
             patch('streamlit.button'):
            
            from app import render_conflict_warning
            render_conflict_warning(conflicts)
            
            call_args = mock_error.call_args[0][0]
            assert '2 contradiction(s)' in call_args
    
    def test_no_ui_when_no_conflicts(self):
        """
        Test that no conflict UI elements are displayed when no conflicts exist.
        
        **Validates: Requirements 7.3**
        """
        conflicts = []
        
        with patch('streamlit.error') as mock_error, \
             patch('streamlit.button') as mock_button:
            
            from app import render_conflict_warning
            render_conflict_warning(conflicts)
            
            # Verify no UI elements were rendered
            mock_error.assert_not_called()
            mock_button.assert_not_called()
    
    def test_no_ui_when_conflicts_is_none(self):
        """Test that no UI elements are displayed when conflicts is None."""
        conflicts = None
        
        with patch('streamlit.error') as mock_error, \
             patch('streamlit.button') as mock_button:
            
            from app import render_conflict_warning
            render_conflict_warning(conflicts)
            
            mock_error.assert_not_called()
            mock_button.assert_not_called()
    
    def test_side_by_side_view_displays_winner_and_rejected(self):
        """
        Test that side-by-side view displays winner and rejected chunks correctly.
        
        **Validates: Requirements 7.2**
        """
        conflict = Conflict(
            winner={
                'content': 'New policy: 60 days refund window',
                'metadata': {
                    'source': 'Policy_v2.pdf',
                    'doc_date': '2024-03-01',
                    'doc_type': 'policy',
                    'section_title': 'Refund Policy',
                    'page_number': 5
                }
            },
            rejected=[{
                'content': 'Old policy: 30 days refund window',
                'metadata': {
                    'source': 'Policy_v1.pdf',
                    'doc_date': '2023-01-15',
                    'doc_type': 'policy',
                    'section_title': 'Refund Policy',
                    'page_number': 3
                }
            }],
            diff_explanation='Refund window changed from 30 to 60 days',
            conflict_type='version_update'
        )
        
        conflicts = [conflict]
        
        with patch('streamlit.divider'), \
             patch('streamlit.subheader') as mock_subheader, \
             patch('streamlit.markdown') as mock_markdown, \
             patch('streamlit.info') as mock_info, \
             patch('streamlit.columns') as mock_columns, \
             patch('streamlit.success') as mock_success, \
             patch('streamlit.warning') as mock_warning, \
             patch('streamlit.container'):
            
            # Mock columns to return mock column objects
            mock_col1 = MagicMock()
            mock_col2 = MagicMock()
            mock_columns.return_value = [mock_col1, mock_col2]
            
            from app import render_side_by_side_conflict_view
            render_side_by_side_conflict_view(conflicts)
            
            # Verify subheader was called
            mock_subheader.assert_called()
            
            # Verify diff explanation was displayed
            mock_info.assert_called()
            info_call = mock_info.call_args[0][0]
            assert 'Refund window changed from 30 to 60 days' in info_call
            
            # Verify markdown was called with metadata
            markdown_calls = [str(call) for call in mock_markdown.call_args_list]
            markdown_text = ' '.join(markdown_calls)
            
            # Check winner metadata
            assert 'Policy_v2.pdf' in markdown_text
            assert '2024-03-01' in markdown_text
            
            # Check rejected metadata
            assert 'Policy_v1.pdf' in markdown_text
            assert '2023-01-15' in markdown_text
    
    def test_side_by_side_view_displays_pdf_metadata(self):
        """Test that PDF-specific metadata (section, page) is displayed."""
        conflict = Conflict(
            winner={
                'content': 'Content',
                'metadata': {
                    'source': 'doc.pdf',
                    'doc_date': '2024-01-01',
                    'doc_type': 'policy',
                    'section_title': 'Section 3.2',
                    'page_number': 10
                }
            },
            rejected=[{
                'content': 'Old content',
                'metadata': {
                    'source': 'old.pdf',
                    'doc_date': '2023-01-01',
                    'doc_type': 'policy',
                    'section_title': 'Section 3.2',
                    'page_number': 8
                }
            }],
            diff_explanation='Updated',
            conflict_type='version_update'
        )
        
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
            render_side_by_side_conflict_view([conflict])
            
            # Verify section and page metadata was displayed
            markdown_calls = [str(call) for call in mock_markdown.call_args_list]
            markdown_text = ' '.join(markdown_calls)
            
            assert 'Section 3.2' in markdown_text
            assert 'Page' in markdown_text
    
    def test_side_by_side_view_displays_excel_metadata(self):
        """Test that Excel-specific metadata (sheet, row) is displayed."""
        conflict = Conflict(
            winner={
                'content': 'Client: Acme, Price: $500',
                'metadata': {
                    'source': 'pricing.xlsx',
                    'doc_date': '2024-01-01',
                    'doc_type': 'excel',
                    'sheet_name': 'Q1 Pricing',
                    'row_number': 42
                }
            },
            rejected=[{
                'content': 'Client: Acme, Price: $400',
                'metadata': {
                    'source': 'pricing_old.xlsx',
                    'doc_date': '2023-01-01',
                    'doc_type': 'excel',
                    'sheet_name': 'Q4 Pricing',
                    'row_number': 38
                }
            }],
            diff_explanation='Price updated',
            conflict_type='version_update'
        )
        
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
            render_side_by_side_conflict_view([conflict])
            
            markdown_calls = [str(call) for call in mock_markdown.call_args_list]
            markdown_text = ' '.join(markdown_calls)
            
            assert 'Sheet' in markdown_text
            assert 'Q1 Pricing' in markdown_text
            assert 'Row' in markdown_text
    
    def test_side_by_side_view_displays_email_metadata(self):
        """Test that email-specific metadata (sender, subject) is displayed."""
        conflict = Conflict(
            winner={
                'content': 'New discount policy',
                'metadata': {
                    'source': 'email',
                    'doc_date': '2024-01-01',
                    'doc_type': 'email',
                    'sender': 'manager@company.com',
                    'subject': 'Updated discount policy'
                }
            },
            rejected=[{
                'content': 'Old discount policy',
                'metadata': {
                    'source': 'email',
                    'doc_date': '2023-01-01',
                    'doc_type': 'email',
                    'sender': 'sales@company.com',
                    'subject': 'Discount policy'
                }
            }],
            diff_explanation='Policy updated',
            conflict_type='cross_doc_type'
        )
        
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
            render_side_by_side_conflict_view([conflict])
            
            markdown_calls = [str(call) for call in mock_markdown.call_args_list]
            markdown_text = ' '.join(markdown_calls)
            
            assert 'From' in markdown_text
            assert 'manager@company.com' in markdown_text
            assert 'Subject' in markdown_text
            assert 'Updated discount policy' in markdown_text
    
    def test_side_by_side_view_displays_multiple_rejected_chunks(self):
        """Test that multiple rejected chunks are displayed correctly."""
        conflict = Conflict(
            winner={
                'content': 'Latest version',
                'metadata': {
                    'source': 'v3.pdf',
                    'doc_date': '2024-03-01',
                    'doc_type': 'policy'
                }
            },
            rejected=[
                {
                    'content': 'Version 2',
                    'metadata': {
                        'source': 'v2.pdf',
                        'doc_date': '2024-02-01',
                        'doc_type': 'policy'
                    }
                },
                {
                    'content': 'Version 1',
                    'metadata': {
                        'source': 'v1.pdf',
                        'doc_date': '2024-01-01',
                        'doc_type': 'policy'
                    }
                }
            ],
            diff_explanation='Multiple updates',
            conflict_type='version_update'
        )
        
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
            render_side_by_side_conflict_view([conflict])
            
            markdown_calls = [str(call) for call in mock_markdown.call_args_list]
            markdown_text = ' '.join(markdown_calls)
            
            # Verify all rejected versions are mentioned
            assert 'v2.pdf' in markdown_text
            assert 'v1.pdf' in markdown_text
            assert 'Rejected version' in markdown_text
    
    def test_side_by_side_view_highlights_differences(self):
        """
        Test that differences between winner and rejected are highlighted.
        
        **Validates: Requirements 7.2**
        """
        conflict = Conflict(
            winner={
                'content': 'Refund window is 60 days',
                'metadata': {
                    'source': 'new.pdf',
                    'doc_date': '2024-01-01',
                    'doc_type': 'policy'
                }
            },
            rejected=[{
                'content': 'Refund window is 30 days',
                'metadata': {
                    'source': 'old.pdf',
                    'doc_date': '2023-01-01',
                    'doc_type': 'policy'
                }
            }],
            diff_explanation='Refund window changed from 30 to 60 days',
            conflict_type='policy_change'
        )
        
        with patch('streamlit.divider'), \
             patch('streamlit.subheader'), \
             patch('streamlit.markdown'), \
             patch('streamlit.info') as mock_info, \
             patch('streamlit.columns') as mock_columns, \
             patch('streamlit.success') as mock_success, \
             patch('streamlit.warning') as mock_warning, \
             patch('streamlit.container'):
            
            mock_col1 = MagicMock()
            mock_col2 = MagicMock()
            mock_columns.return_value = [mock_col1, mock_col2]
            
            from app import render_side_by_side_conflict_view
            render_side_by_side_conflict_view([conflict])
            
            # Verify diff explanation is displayed
            mock_info.assert_called()
            info_text = mock_info.call_args[0][0]
            assert 'Refund window changed from 30 to 60 days' in info_text
            
            # Verify winner content is displayed in success (green)
            mock_success.assert_called()
            success_text = mock_success.call_args[0][0]
            assert 'Refund window is 60 days' in success_text
            
            # Verify rejected content is displayed in warning (yellow/orange)
            mock_warning.assert_called()
            warning_text = mock_warning.call_args[0][0]
            assert 'Refund window is 30 days' in warning_text
    
    def test_query_interface_integrates_conflict_detection(self):
        """Test that query interface calls conflict detection and displays warning."""
        with patch('streamlit.text_input', return_value='test query'), \
             patch('streamlit.button', return_value=True), \
             patch('streamlit.spinner'), \
             patch('streamlit.write'), \
             patch('streamlit.success'), \
             patch('streamlit.caption'), \
             patch('streamlit.divider'), \
             patch('streamlit.subheader'), \
             patch('streamlit.expander'), \
             patch('os.getenv', return_value='test-key'), \
             patch('storage.chroma_store.init_chroma_collection') as mock_init, \
             patch('retrieval.query_engine.create_query_engine') as mock_engine, \
             patch('retrieval.query_engine.query_with_metadata') as mock_query, \
             patch('retrieval.conflict_detector.detect_conflicts') as mock_detect, \
             patch('app.render_conflict_warning') as mock_render_warning, \
             patch('app.render_citation'):
            
            # Mock collection
            mock_collection = Mock()
            mock_collection.count.return_value = 10
            mock_init.return_value = (Mock(), mock_collection)
            
            # Mock query result
            mock_result = Mock()
            mock_result.answer = 'Test answer'
            mock_result.source_chunks = []
            mock_result.response_time_ms = 100
            mock_query.return_value = mock_result
            
            # Mock conflicts
            mock_conflicts = [Mock()]
            mock_detect.return_value = mock_conflicts
            
            from app import render_query_interface
            render_query_interface()
            
            # Verify conflict detection was called
            mock_detect.assert_called_once_with(mock_result.source_chunks)
            
            # Verify conflict warning was rendered
            mock_render_warning.assert_called_once_with(mock_conflicts)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
