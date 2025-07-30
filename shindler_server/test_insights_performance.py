#!/usr/bin/env python3
"""
Performance Test Script for AI Insights Session Optimization
Tests the performance improvements from using single session per insights request
"""

import time
import statistics
from datetime import datetime, timedelta
import logging

# Import KPI services
from kpis.ei_tech_kpis import EITechKPIQueries
from kpis.srs_kpis import SRSKPIQueries
from kpis.ni_tct_kpis import NITCTKPIQueries

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InsightsPerformanceTester:
    """Test insights KPI performance with session optimization"""
    
    def __init__(self):
        # Test parameters
        self.end_date = datetime.now().strftime("%Y-%m-%d")
        self.start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        
    def time_kpi_request_old_way(self, kpi_service, service_name):
        """Time KPI request using old method (multiple sessions)"""
        start_time = time.time()
        
        try:
            # Old way: each KPI method creates its own session
            result = kpi_service.get_all_kpis()  # No session parameter
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Count KPIs returned
            kpi_count = len(result) if isinstance(result, dict) else 0
            
            logger.info(f"{service_name} KPIs (OLD WAY) completed in {duration:.3f}s with {kpi_count} KPIs")
            
            return {
                'service': service_name,
                'method': 'old_way',
                'duration': duration,
                'kpi_count': kpi_count,
                'success': True
            }
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            logger.error(f"{service_name} KPIs (OLD WAY) failed after {duration:.3f}s: {e}")
            
            return {
                'service': service_name,
                'method': 'old_way',
                'duration': duration,
                'kpi_count': 0,
                'success': False,
                'error': str(e)
            }
    
    def time_kpi_request_new_way(self, kpi_service, service_name):
        """Time KPI request using new method (single session)"""
        start_time = time.time()
        
        try:
            # New way: single session for all KPI methods
            session = kpi_service.get_session()
            try:
                result = kpi_service.get_all_kpis(session)  # With session parameter
            finally:
                session.close()
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Count KPIs returned
            kpi_count = len(result) if isinstance(result, dict) else 0
            
            logger.info(f"{service_name} KPIs (NEW WAY) completed in {duration:.3f}s with {kpi_count} KPIs")
            
            return {
                'service': service_name,
                'method': 'new_way',
                'duration': duration,
                'kpi_count': kpi_count,
                'success': True
            }
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            logger.error(f"{service_name} KPIs (NEW WAY) failed after {duration:.3f}s: {e}")
            
            return {
                'service': service_name,
                'method': 'new_way',
                'duration': duration,
                'kpi_count': 0,
                'success': False,
                'error': str(e)
            }
    
    def run_performance_comparison(self, iterations=3):
        """Run performance comparison between old and new methods"""
        logger.info(f"Starting insights KPI performance comparison with {iterations} iterations")
        logger.info(f"Date range: {self.start_date} to {self.end_date}")
        
        results = {
            'ei_tech': {'old_way': [], 'new_way': []},
            'srs': {'old_way': [], 'new_way': []},
            'ni_tct': {'old_way': [], 'new_way': []}
        }
        
        # Test services
        services = [
            (EITechKPIQueries(start_date=self.start_date, end_date=self.end_date), 'ei_tech'),
            (SRSKPIQueries(), 'srs'),
            (NITCTKPIQueries(start_date=self.start_date, end_date=self.end_date), 'ni_tct')
        ]
        
        for iteration in range(iterations):
            logger.info(f"\n--- Iteration {iteration + 1}/{iterations} ---")
            
            for kpi_service, service_name in services:
                # Test old way (multiple sessions)
                old_result = self.time_kpi_request_old_way(kpi_service, service_name)
                results[service_name]['old_way'].append(old_result)
                
                # Small delay
                time.sleep(1)
                
                # Test new way (single session)
                new_result = self.time_kpi_request_new_way(kpi_service, service_name)
                results[service_name]['new_way'].append(new_result)
                
                # Small delay between services
                time.sleep(1)
        
        return results
    
    def analyze_performance_improvements(self, results):
        """Analyze and report performance improvements"""
        logger.info("\n" + "="*70)
        logger.info("AI INSIGHTS KPI PERFORMANCE ANALYSIS")
        logger.info("="*70)
        
        total_improvement = 0
        service_count = 0
        
        for service_name, service_results in results.items():
            old_results = [r for r in service_results['old_way'] if r['success']]
            new_results = [r for r in service_results['new_way'] if r['success']]
            
            if not old_results or not new_results:
                logger.warning(f"{service_name.upper()}: Insufficient successful results for comparison!")
                continue
            
            old_durations = [r['duration'] for r in old_results]
            new_durations = [r['duration'] for r in new_results]
            
            old_avg = statistics.mean(old_durations)
            new_avg = statistics.mean(new_durations)
            
            improvement_pct = ((old_avg - new_avg) / old_avg) * 100
            total_improvement += improvement_pct
            service_count += 1
            
            old_kpi_count = statistics.mean([r['kpi_count'] for r in old_results])
            estimated_old_sessions = old_kpi_count  # Approximate sessions before optimization
            estimated_new_sessions = 1  # One session after optimization
            
            logger.info(f"\n{service_name.upper()} KPI Performance:")
            logger.info(f"  Old method (multiple sessions):")
            logger.info(f"    Average duration: {old_avg:.3f}s")
            logger.info(f"    Estimated sessions: ~{estimated_old_sessions:.0f}")
            logger.info(f"  New method (single session):")
            logger.info(f"    Average duration: {new_avg:.3f}s")
            logger.info(f"    Sessions used: {estimated_new_sessions}")
            logger.info(f"  Performance improvement: {improvement_pct:.1f}%")
            logger.info(f"  Session reduction: {((estimated_old_sessions - estimated_new_sessions) / estimated_old_sessions) * 100:.1f}%")
            logger.info(f"  Time saved per request: {old_avg - new_avg:.3f}s")
        
        # Overall summary
        if service_count > 0:
            avg_improvement = total_improvement / service_count
            logger.info(f"\nOVERALL INSIGHTS PERFORMANCE:")
            logger.info(f"  Average performance improvement: {avg_improvement:.1f}%")
            logger.info(f"  Services optimized: {service_count}")
            
            if avg_improvement > 0:
                logger.info(f"  🚀 OPTIMIZATION SUCCESSFUL! {avg_improvement:.1f}% faster insights generation")
            else:
                logger.warning(f"  ⚠️  Performance regression detected: {abs(avg_improvement):.1f}% slower")
        
        logger.info("\n" + "="*70)

def main():
    """Main test function"""
    tester = InsightsPerformanceTester()
    
    # Run performance comparison
    results = tester.run_performance_comparison(iterations=3)
    
    # Analyze improvements
    tester.analyze_performance_improvements(results)
    
    logger.info("\nInsights performance test completed!")

if __name__ == "__main__":
    main()
