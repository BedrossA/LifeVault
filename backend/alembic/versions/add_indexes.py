from alembic import op
def upgrade():
    # Add indexes for analytics queries
    op.create_index(
        'idx_analytics_user_timestamp',
        'analytics_entries',
        ['user_id', 'timestamp']
    )
    
    op.create_index(
        'idx_analytics_category_metric',
        'analytics_entries',
        ['category', 'metric']
    )
    
    # Add index for face recognition
    op.create_index(
        'idx_faces_user_active',
        'faces',
        ['user_id', 'is_active']
    )