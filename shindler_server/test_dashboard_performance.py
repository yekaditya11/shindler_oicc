#!/usr/bin/env python3
"""
Performance Test Script for Dashboard Session Optimization
Tests the performance improvements from using single session per dashboard request
"""

import time
import asyncio
import statistics
from datetime import datetime, timedelta
import logging

# Import dashboard services
from dashboard.ei_tech_dashboard_service import EITechDashboardService
from dashboard.srs_dashboard_service import SRSDashboardService
from dashboard.ni_tct_dashboard_service import NITCTDashboardService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardPerformanceTester:
    """Test dashboard performance with session optimization"""
    
    def __init__(self):
        self.ei_tech_service = EITechDashboardService()
        self.srs_service = SRSDashboardService()
        self.ni_tct_service = NITCTDashboardService()
        
        # Test parameters
        self.end_date = datetime.now().strftime("%Y-%m-%d")
        self.start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        
    def time_dashboard_request(self, service, service_name):
        """Time a single dashboard request"""
        start_time = time.time()
        
        try:
            result = service.get_dashboard_data(
                start_date=self.start_date,
                end_date=self.end_date
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Count KPIs returned
            kpi_count = len(result.get('dashboard_data', {}))
            
            logger.info(f"{service_name} dashboard completed in {duration:.3f}s with {kpi_count} KPIs")
            
            return {
                'service': service_name,
                'duration': duration,
                'kpi_count': kpi_count,
                'success': True
            }
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            logger.error(f"{service_name} dashboard failed after {duration:.3f}s: {e}")
            
            return {
                'service': service_name,
                'duration': duration,
                'kpi_count': 0,
                'success': False,
                'error': str(e)
            }
    
    def run_performance_test(self, iterations=5):
        """Run performance test with multiple iterations"""
        logger.info(f"Starting dashboard performance test with {iterations} iterations")
        logger.info(f"Date range: {self.start_date} to {self.end_date}")
        
        results = {
            'ei_tech': [],
            'srs': [],
            'ni_tct': []
        }
        
        # Test each dashboard service
        services = [
            (self.ei_tech_service, 'ei_tech'),
            (self.srs_service, 'srs'),
            (self.ni_tct_service, 'ni_tct')
        ]
        
        for iteration in range(iterations):
            logger.info(f"\n--- Iteration {iteration + 1}/{iterations} ---")
            
            for service, service_name in services:
                result = self.time_dashboard_request(service, service_name)
                results[service_name].append(result)
                
                # Small delay between requests
                time.sleep(0.5)
        
        return results
    
    def analyze_results(self, results):
        """Analyze and report performance results"""
        logger.info("\n" + "="*60)
        logger.info("DASHBOARD PERFORMANCE ANALYSIS")
        logger.info("="*60)
        
        for service_name, service_results in results.items():
            successful_results = [r for r in service_results if r['success']]
            
            if not successful_results:
                logger.warning(f"{service_name.upper()}: All requests failed!")
                continue
            
            durations = [r['duration'] for r in successful_results]
            kpi_counts = [r['kpi_count'] for r in successful_results]
            
            avg_duration = statistics.mean(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            median_duration = statistics.median(durations)
            
            avg_kpi_count = statistics.mean(kpi_counts)
            
            logger.info(f"\n{service_name.upper()} Dashboard Performance:")
            logger.info(f"  Successful requests: {len(successful_results)}/{len(service_results)}")
            logger.info(f"  Average duration: {avg_duration:.3f}s")
            logger.info(f"  Median duration: {median_duration:.3f}s")
            logger.info(f"  Min duration: {min_duration:.3f}s")
            logger.info(f"  Max duration: {max_duration:.3f}s")
            logger.info(f"  Average KPIs returned: {avg_kpi_count:.1f}")
            
            # Calculate performance metrics
            kpis_per_second = avg_kpi_count / avg_duration
            logger.info(f"  KPIs per second: {kpis_per_second:.2f}")
            
            # Estimate session savings
            estimated_old_sessions = avg_kpi_count  # One session per KPI before optimization
            estimated_new_sessions = 1  # One session per dashboard after optimization
            session_reduction = ((estimated_old_sessions - estimated_new_sessions) / estimated_old_sessions) * 100
            
            logger.info(f"  Estimated session reduction: {session_reduction:.1f}%")
            logger.info(f"  Sessions before optimization: ~{estimated_old_sessions:.0f}")
            logger.info(f"  Sessions after optimization: {estimated_new_sessions}")
        
        # Overall summary
        all_successful = []
        for service_results in results.values():
            all_successful.extend([r for r in service_results if r['success']])
        
        if all_successful:
            total_requests = len(all_successful)
            total_kpis = sum(r['kpi_count'] for r in all_successful)
            total_duration = sum(r['duration'] for r in all_successful)
            
            logger.info(f"\nOVERALL PERFORMANCE:")
            logger.info(f"  Total successful requests: {total_requests}")
            logger.info(f"  Total KPIs processed: {total_kpis}")
            logger.info(f"  Total processing time: {total_duration:.3f}s")
            logger.info(f"  Average KPIs per request: {total_kpis/total_requests:.1f}")
            logger.info(f"  Overall KPIs per second: {total_kpis/total_duration:.2f}")
        
        logger.info("\n" + "="*60)

def main():
    """Main test function"""
    tester = DashboardPerformanceTester()
    
    # Run performance test
    results = tester.run_performance_test(iterations=3)
    
    # Analyze results
    tester.analyze_results(results)
    
    logger.info("\nPerformance test completed!")

if __name__ == "__main__":
    main()
