# HubSpot v3 API Migration

This document outlines the migration of the tap-hubspot codebase from HubSpot's deprecated v1/v2 APIs to the new v3 APIs.

## Overview

The migration includes:
- **Complete API endpoint updates** from v1/v2 to v3
- **Cursor-based pagination** instead of offset-based
- **Updated schemas** to match v3 response structures
- **New primary keys** (from vid/companyId/dealId to id)
- **Standardized bookmark fields** (updatedAt, occurredAt)
- **Enhanced checkpointing** for all streams
- **New events stream** with Custom Events API support

## Breaking Changes

### Primary Key Changes
- **Contacts**: `vid` → `id`
- **Companies**: `companyId` → `id`
- **Deals**: `dealId` → `id`
- **Tickets**: `ticketId` → `id`
- **Forms**: `guid` → `id`
- **Contact Lists**: `listId` → `id`
- **Engagements**: `engagement_id` → `id`
- **Campaigns**: `id` (unchanged)
- **Deal Pipelines**: `pipelineId` → `id`

### Bookmark Field Changes
- **Contacts**: `property_hs_lastmodifieddate` → `updatedAt`
- **Companies**: `property_hs_lastmodifieddate` → `updatedAt`
- **Deals**: `property_hs_lastmodifieddate` → `updatedAt`
- **Tickets**: `property_hs_lastmodifieddate` → `updatedAt`
- **Forms**: `property_hs_lastmodifieddate` → `updatedAt`
- **Contact Lists**: `property_hs_lastmodifieddate` → `updatedAt`
- **Engagements**: `lastUpdated` → `updatedAt`
- **Campaigns**: `updatedAt` (new)
- **Deal Pipelines**: `updatedAt` (new)
- **Events**: `occurredAt` (new)

### Replication Method Changes
- **Campaigns**: `FULL_TABLE` → `INCREMENTAL`
- **Deal Pipelines**: `FULL_TABLE` → `INCREMENTAL`

## Enhanced Checkpointing

All streams now properly implement checkpointing using the `start_date` parameter from `config.json`:

### Events Stream Checkpointing
The events stream uses the `occurredAfter` parameter as documented in the [HubSpot Event Analytics API](https://developers.hubspot.com/docs/reference/api/analytics-and-events/event-analytics):

```python
# Add checkpointing using occurredAfter parameter
if start:
    occurred_after_ms = int(start.timestamp() * 1000)
    params['occurredAfter'] = occurred_after_ms
```

### Standard Stream Checkpointing
All other streams use the `after` parameter for cursor-based pagination with checkpointing:

```python
# Use v3 API pagination with cursor-based approach
if start:
    params['after'] = int(start.timestamp() * 1000)  # Convert to milliseconds
```

### Race Condition Protection
All incremental streams include protection against race conditions by storing the current sync start time and not moving bookmarks past this value:

```python
# Because this stream doesn't query by `updatedAt`, it cycles
# through the data set every time. The issue with this is that there
# is a race condition by which records may be updated between the
# start of this table's sync and the end, causing some updates to not
# be captured, in order to combat this, we must store the current
# sync's start in the state and not move the bookmark past this value.
current_sync_start = get_current_sync_start(STATE, stream_name) or utils.now()
STATE = write_current_sync_start(STATE, stream_name, current_sync_start)
```

## New Events Stream

### API Endpoints
- **Event Definitions**: `/events/v3/event-definitions`
- **Events**: `/events/v3/events`

### Schema
The events stream includes:
- `id`: Unique event identifier
- `eventType`: Type of event (e.g., "page_view", "form_submit")
- `occurredAt`: Timestamp when event occurred
- `properties`: Event-specific properties
- `contactId`: Associated contact ID
- `companyId`: Associated company ID
- `dealId`: Associated deal ID
- `ticketId`: Associated ticket ID

### Checkpointing
Events use `occurredAt` as the bookmark field and `occurredAfter` parameter for incremental sync:

```python
bookmark_key = 'occurredAt'
# Add checkpointing using occurredAfter parameter
if start:
    occurred_after_ms = int(start.timestamp() * 1000)
    params['occurredAfter'] = occurred_after_ms
```

## Updated Endpoints

### Core CRM Objects
- **Contacts**: `/crm/v3/objects/contacts`
- **Companies**: `/crm/v3/objects/companies`
- **Deals**: `/crm/v3/objects/deals`
- **Tickets**: `/crm/v3/objects/tickets`

### Marketing Objects
- **Forms**: `/crm/v3/objects/forms`
- **Contact Lists**: `/crm/v3/objects/contact_lists`
- **Campaigns**: `/crm/v3/objects/campaigns`
- **Engagements**: `/crm/v3/objects/engagements`

### Automation & Workflows
- **Workflows**: `/automation/v4/workflows`
- **Deal Pipelines**: `/crm/v3/pipelines/deals`
- **Owners**: `/crm/v3/owners`

### Events & Analytics
- **Event Definitions**: `/events/v3/event-definitions`
- **Events**: `/events/v3/events`

## Configuration

### Required Configuration
```json
{
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "refresh_token": "your_refresh_token",
  "start_date": "2024-01-01T00:00:00Z"
}
```

### Optional Configuration
```json
{
  "request_timeout": 300,
  "email_chunk_size": 86400000,
  "subscription_chunk_size": 86400000
}
```

## Testing

### Test Script
Use the provided test script to verify the migration:

```bash
python test_v3_migration.py
```

The test script includes:
- OAuth token acquisition testing
- All v3 API endpoint testing
- Checkpointing functionality testing
- Sample data output

### Checkpointing Tests
The test script specifically tests checkpointing with:
- Events using `occurredAfter` parameter
- Contacts using `after` parameter
- Companies using `after` parameter
- Deals using `after` parameter

## Benefits of v3 Migration

### Performance Improvements
- **Cursor-based pagination** is more efficient than offset-based
- **Reduced API calls** through better pagination
- **Faster sync times** with optimized endpoints

### Enhanced Reliability
- **Better error handling** with standardized responses
- **Improved rate limiting** support
- **Consistent data structures** across all endpoints

### New Features
- **Events stream** for analytics and tracking
- **Enhanced checkpointing** for all streams
- **Better association handling** with standardized formats
- **Archived record support** with `archived` parameter

### Future-Proofing
- **Long-term API support** (v1/v2 are deprecated)
- **Access to new features** only available in v3
- **Better documentation** and community support

## Migration Checklist

- [x] Update all API endpoints to v3
- [x] Implement cursor-based pagination
- [x] Update schemas for v3 response structure
- [x] Change primary keys to `id`
- [x] Standardize bookmark fields
- [x] Add events stream with Custom Events API
- [x] Implement enhanced checkpointing for all streams
- [x] Update replication methods (FULL_TABLE → INCREMENTAL)
- [x] Add race condition protection
- [x] Create comprehensive test script
- [x] Update documentation

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify `client_id`, `client_secret`, and `refresh_token`
   - Ensure OAuth app has correct scopes

2. **Rate Limiting**
   - Implement exponential backoff
   - Check HubSpot rate limits documentation

3. **Schema Mismatches**
   - Verify schema files match v3 API responses
   - Check for new required fields

4. **Checkpointing Issues**
   - Verify `start_date` format (ISO 8601)
   - Check bookmark field names match v3 API

### Debug Mode
Enable debug logging by setting the log level to DEBUG in your configuration.

## Support

For issues related to:
- **HubSpot API**: Check [HubSpot Developer Documentation](https://developers.hubspot.com/)
- **Singer Framework**: Check [Singer Documentation](https://github.com/singer-io/getting-started)
- **This Migration**: Check this README and the test script