from datetime import datetime
from sqlalchemy import func
from app.models.pages.company import Company
from app.models.base import db


class CompanyService:
    def get_total_companies(self):
        """Get the total number of companies"""
        return Company.query.count()

    def get_dashboard_stats(self):
        """Get statistics for the companies dashboard"""
        total_companies = self.get_total_companies()

        return {
            "total_companies": total_companies,
            "with_opportunities": db.session.query(Company).filter(Company.opportunities.any()).count(),
            "with_contacts": db.session.query(Company).filter(Company.contacts.any()).count(),
            "with_capabilities": db.session.query(Company).filter(Company.company_capabilities.any()).count(),
        }

    def get_top_companies(self, limit=5):
        """Get top companies by opportunity count"""
        return (
            db.session.query(Company, func.count(Company.opportunities).label("opportunity_count"))
            .outerjoin(Company.opportunities)
            .group_by(Company.id)
            .order_by(func.count(Company.opportunities).desc())
            .limit(limit)
            .all()
        )

    def get_engagement_segments(self):
        """Get company segments by engagement level"""
        total_companies = self.get_total_companies()

        # High engagement (>2 opportunities)
        high_engagement_count = (
            db.session.query(Company)
            .join(Company.opportunities)
            .group_by(Company.id)
            .having(func.count(Company.opportunities) > 2)
            .count()
        )

        # Medium engagement (1-2 opportunities)
        medium_engagement_count = (
            db.session.query(Company)
            .join(Company.opportunities)
            .group_by(Company.id)
            .having(func.count(Company.opportunities).between(1, 2))
            .count()
        )

        # No opportunities
        no_opportunities_count = (
            db.session.query(Company)
            .outerjoin(Company.opportunities)
            .group_by(Company.id)
            .having(func.count(Company.opportunities) == 0)
            .count()
        )

        return [
            {
                "name": "High Engagement",
                "count": high_engagement_count,
                "percentage": self._calculate_percentage(high_engagement_count, total_companies),
            },
            {
                "name": "Medium Engagement",
                "count": medium_engagement_count,
                "percentage": self._calculate_percentage(medium_engagement_count, total_companies),
            },
            {
                "name": "No Opportunities",
                "count": no_opportunities_count,
                "percentage": self._calculate_percentage(no_opportunities_count, total_companies),
            },
        ]

    def prepare_growth_data(self, months_back=6):
        """Prepare growth data for the chart"""
        months = []
        new_companies = []
        total_companies = []

        current_month = datetime.now().month
        current_year = datetime.now().year

        for i in range(months_back):
            month = (current_month - i) % 12
            if month == 0:
                month = 12
            year = current_year - ((current_month - i) // 12)

            # Month name for label
            month_name = datetime(year, month, 1).strftime("%b %Y")

            # Start of month date
            start_date = datetime(year, month, 1)

            # End of month date - first day of next month
            next_month = month + 1 if month < 12 else 1
            next_year = year if month < 12 else year + 1
            end_date = datetime(next_year, next_month, 1)

            # Previous month end for calculating cumulative
            if i < months_back - 1:
                prev_end = start_date
            else:
                # For the oldest month, just use a reasonable past date
                prev_end = datetime(year - 1, month, 1)

            # New companies in this month
            new_in_month = (
                Company.query
                .filter(Company.created_at >= start_date, Company.created_at < end_date)
                .count()
            )

            # Total companies at end of month
            total_at_month_end = (
                Company.query
                .filter(Company.created_at < end_date)
                .count()
            )

            months.append(month_name)
            new_companies.append(new_in_month)
            total_companies.append(total_at_month_end)

        # Reverse lists to display chronologically
        months.reverse()
        new_companies.reverse()
        total_companies.reverse()

        return {
            "labels": months,
            "new_companies": new_companies,
            "total_companies": total_companies
        }

    def get_filtered_companies(self, filters):
        """Get companies based on filter criteria"""
        query = Company.query

        # Filter by opportunities
        if filters.get("has_opportunities") == "yes":
            query = query.filter(Company.opportunities.any())
        elif filters.get("has_opportunities") == "no":
            query = query.filter(~Company.opportunities.any())

        # Filter by contacts
        if filters.get("has_contacts") == "yes":
            query = query.filter(Company.contacts.any())
        elif filters.get("has_contacts") == "no":
            query = query.filter(~Company.contacts.any())

        # Filter by capabilities
        if filters.get("has_capabilities") == "yes":
            query = query.filter(Company.company_capabilities.any())
        elif filters.get("has_capabilities") == "no":
            query = query.filter(~Company.company_capabilities.any())

        return query.order_by(Company.name.asc()).all()

    def get_statistics(self):
        """Get comprehensive statistics for the statistics page"""
        total_companies = self.get_total_companies()

        # Companies with opportunities
        with_opportunities = db.session.query(Company).filter(Company.opportunities.any()).count()

        # Companies with contacts
        with_contacts = db.session.query(Company).filter(Company.contacts.any()).count()

        # Companies with no engagement
        no_engagement = (
            db.session.query(Company)
            .outerjoin(Company.opportunities)
            .outerjoin(Company.contacts)
            .group_by(Company.id)
            .having(func.count(Company.opportunities) == 0, func.count(Company.contacts) == 0)
            .count()
        )

        return {
            "total_companies": total_companies,
            "with_opportunities": with_opportunities,
            "with_contacts": with_contacts,
            "no_engagement": no_engagement,
        }

    def get_company_by_id(self, company_id):
        """Get a company by ID"""
        return Company.query.get(company_id)

    def _calculate_percentage(self, count, total):
        """Calculate percentage with safety check for division by zero"""
        if total == 0:
            return 0
        return round((count / total) * 100)