# Acme Corp Internal Cloud Security Policies

This document outlines the internal security policies that all AWS accounts and IAM resources must adhere to.

## 1. Access Key Management
- Access keys must be rotated strictly every **90 days**. 
- Any access key older than 90 days is a **HIGH** severity violation.
- Inactive access keys must be deleted after 30 days of inactivity.

## 2. Multi-Factor Authentication (MFA)
- **All** human IAM users MUST have MFA enabled.
- Exception: The `legacy-backup-service` user is a machine account and is permanently exempt from the MFA requirement.

## 3. Least Privilege & Wildcards
- The `AdministratorAccess` AWS managed policy is strictly forbidden for human users. It may only be attached to approved CI/CD pipeline roles.
- No IAM policy may contain a `*` (wildcard) in the `Action` field, except for read-only actions like `s3:Get*` or `s3:List*`.

## 4. Approved Services
- The use of `iam:PassRole` is heavily restricted and any policy granting it without a strict `Resource` constraint is a **CRITICAL** violation.

## 5. Passwords
- Console passwords must be rotated every 90 days.
