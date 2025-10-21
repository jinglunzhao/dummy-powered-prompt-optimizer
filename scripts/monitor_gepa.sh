#!/bin/bash
# Monitor GEPA optimization progress

echo "🔍 GEPA Test Monitor"
echo "===================="
echo ""

# Check if process is running
if pgrep -f "test_gepa_system.py" > /dev/null; then
    echo "✅ Test is RUNNING"
    echo ""
else
    echo "❌ Test is NOT running"
    echo ""
fi

# Show latest log entries
echo "📊 Latest Progress:"
echo "-------------------"
tail -20 gepa_test_full.log
echo ""

# Extract key metrics
echo "📈 Quick Stats:"
echo "-------------------"
grep "Generation" gepa_test_full.log | tail -5
grep "completed baseline assessment" gepa_test_full.log | wc -l | xargs -I {} echo "Baseline assessments: {}"
grep "Natural ending detected" gepa_test_full.log | wc -l | xargs -I {} echo "Completed conversations: {}"
grep "Materialized" gepa_test_full.log | wc -l | xargs -I {} echo "Personality materializations: {}"
echo ""

# Estimated completion
echo "⏱️  Estimated total time: ~15 hours (900 minutes)"
echo "💡 Use 'tail -f gepa_test_full.log' to watch live progress"


