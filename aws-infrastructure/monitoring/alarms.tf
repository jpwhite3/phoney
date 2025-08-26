# CloudWatch Alarms for Phoney Serverless Application

# SNS Topic for alerting
resource "aws_sns_topic" "phoney_alerts" {
  name = "phoney-${var.stage}-alerts"
  
  tags = {
    Project = "Phoney"
    Stage   = var.stage
  }
}

# SNS Topic Subscription (replace with your email)
resource "aws_sns_topic_subscription" "email_alerts" {
  topic_arn = aws_sns_topic.phoney_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email # Set this variable
}

# Lambda Function Error Rate Alarm
resource "aws_cloudwatch_metric_alarm" "lambda_error_rate" {
  alarm_name          = "phoney-${var.stage}-lambda-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = var.stage == "prod" ? "5" : "10"
  alarm_description   = "This metric monitors lambda error rate"
  alarm_actions       = [aws_sns_topic.phoney_alerts.arn]
  ok_actions          = [aws_sns_topic.phoney_alerts.arn]

  dimensions = {
    FunctionName = "phoney-${var.stage}"
  }

  tags = {
    Project = "Phoney"
    Stage   = var.stage
  }
}

# Lambda Function Duration Alarm
resource "aws_cloudwatch_metric_alarm" "lambda_duration" {
  alarm_name          = "phoney-${var.stage}-lambda-duration"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Average"
  threshold           = var.stage == "prod" ? "10000" : "15000" # 10s prod, 15s dev/staging
  alarm_description   = "This metric monitors lambda duration"
  alarm_actions       = [aws_sns_topic.phoney_alerts.arn]
  ok_actions          = [aws_sns_topic.phoney_alerts.arn]

  dimensions = {
    FunctionName = "phoney-${var.stage}"
  }

  tags = {
    Project = "Phoney"
    Stage   = var.stage
  }
}

# Lambda Function Throttles Alarm
resource "aws_cloudwatch_metric_alarm" "lambda_throttles" {
  alarm_name          = "phoney-${var.stage}-lambda-throttles"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Throttles"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "This metric monitors lambda throttles"
  alarm_actions       = [aws_sns_topic.phoney_alerts.arn]
  ok_actions          = [aws_sns_topic.phoney_alerts.arn]

  dimensions = {
    FunctionName = "phoney-${var.stage}"
  }

  tags = {
    Project = "Phoney"
    Stage   = var.stage
  }
}

# API Gateway 4XX Error Rate Alarm
resource "aws_cloudwatch_metric_alarm" "api_gateway_4xx" {
  alarm_name          = "phoney-${var.stage}-api-4xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "4XXError"
  namespace           = "AWS/ApiGateway"
  period              = "300"
  statistic           = "Sum"
  threshold           = var.stage == "prod" ? "20" : "50"
  alarm_description   = "This metric monitors API Gateway 4XX errors"
  alarm_actions       = [aws_sns_topic.phoney_alerts.arn]

  dimensions = {
    ApiName = "phoney-api-${var.stage}"
  }

  tags = {
    Project = "Phoney"
    Stage   = var.stage
  }
}

# API Gateway 5XX Error Rate Alarm
resource "aws_cloudwatch_metric_alarm" "api_gateway_5xx" {
  alarm_name          = "phoney-${var.stage}-api-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "5XXError"
  namespace           = "AWS/ApiGateway"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "This metric monitors API Gateway 5XX errors"
  alarm_actions       = [aws_sns_topic.phoney_alerts.arn]
  ok_actions          = [aws_sns_topic.phoney_alerts.arn]

  dimensions = {
    ApiName = "phoney-api-${var.stage}"
  }

  tags = {
    Project = "Phoney"
    Stage   = var.stage
  }
}

# API Gateway Latency Alarm
resource "aws_cloudwatch_metric_alarm" "api_gateway_latency" {
  alarm_name          = "phoney-${var.stage}-api-latency"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "Latency"
  namespace           = "AWS/ApiGateway"
  period              = "300"
  statistic           = "Average"
  threshold           = var.stage == "prod" ? "5000" : "10000" # 5s prod, 10s dev/staging
  alarm_description   = "This metric monitors API Gateway latency"
  alarm_actions       = [aws_sns_topic.phoney_alerts.arn]

  dimensions = {
    ApiName = "phoney-api-${var.stage}"
  }

  tags = {
    Project = "Phoney"
    Stage   = var.stage
  }
}

# Custom Metric: Template Processing Performance
resource "aws_cloudwatch_metric_alarm" "template_processing_performance" {
  alarm_name          = "phoney-${var.stage}-template-processing-slow"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "ExecutionTime"
  namespace           = "Phoney/TemplateAPI"
  period              = "300"
  statistic           = "Average"
  threshold           = "5000" # 5 seconds
  alarm_description   = "This metric monitors template processing performance"
  alarm_actions       = [aws_sns_topic.phoney_alerts.arn]

  tags = {
    Project = "Phoney"
    Stage   = var.stage
  }
}

# Log-based Alarm: Application Errors
resource "aws_cloudwatch_log_metric_filter" "application_errors" {
  name           = "phoney-${var.stage}-application-errors"
  log_group_name = "/aws/lambda/phoney-${var.stage}"
  pattern        = "[timestamp, request_id, level=\"ERROR\", ...]"

  metric_transformation {
    name      = "ApplicationErrors"
    namespace = "Phoney/TemplateAPI"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "application_errors" {
  alarm_name          = "phoney-${var.stage}-application-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ApplicationErrors"
  namespace           = "Phoney/TemplateAPI"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "This metric monitors application-level errors"
  alarm_actions       = [aws_sns_topic.phoney_alerts.arn]
  ok_actions          = [aws_sns_topic.phoney_alerts.arn]

  tags = {
    Project = "Phoney"
    Stage   = var.stage
  }
}

# Composite Alarm: Overall System Health
resource "aws_cloudwatch_composite_alarm" "system_health" {
  alarm_name        = "phoney-${var.stage}-system-health"
  alarm_description = "Overall system health for Phoney application"

  alarm_rule = join(" OR ", [
    "ALARM('${aws_cloudwatch_metric_alarm.lambda_error_rate.alarm_name}')",
    "ALARM('${aws_cloudwatch_metric_alarm.lambda_throttles.alarm_name}')",
    "ALARM('${aws_cloudwatch_metric_alarm.api_gateway_5xx.alarm_name}')",
    "ALARM('${aws_cloudwatch_metric_alarm.application_errors.alarm_name}')"
  ])

  alarm_actions = [aws_sns_topic.phoney_alerts.arn]
  ok_actions    = [aws_sns_topic.phoney_alerts.arn]

  tags = {
    Project = "Phoney"
    Stage   = var.stage
  }
}

# Variables
variable "stage" {
  description = "Deployment stage (dev, staging, prod)"
  type        = string
}

variable "alert_email" {
  description = "Email address for alerts"
  type        = string
}

# Outputs
output "sns_topic_arn" {
  description = "SNS topic ARN for alerts"
  value       = aws_sns_topic.phoney_alerts.arn
}

output "alarms" {
  description = "List of created alarms"
  value = {
    lambda_error_rate    = aws_cloudwatch_metric_alarm.lambda_error_rate.alarm_name
    lambda_duration      = aws_cloudwatch_metric_alarm.lambda_duration.alarm_name
    lambda_throttles     = aws_cloudwatch_metric_alarm.lambda_throttles.alarm_name
    api_4xx              = aws_cloudwatch_metric_alarm.api_gateway_4xx.alarm_name
    api_5xx              = aws_cloudwatch_metric_alarm.api_gateway_5xx.alarm_name
    api_latency          = aws_cloudwatch_metric_alarm.api_gateway_latency.alarm_name
    template_performance = aws_cloudwatch_metric_alarm.template_processing_performance.alarm_name
    application_errors   = aws_cloudwatch_metric_alarm.application_errors.alarm_name
    system_health        = aws_cloudwatch_composite_alarm.system_health.alarm_name
  }
}