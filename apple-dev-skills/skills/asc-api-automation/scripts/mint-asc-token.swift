#!/usr/bin/env swift
//
// mint-asc-token.swift — mint a short-lived App Store Connect API JWT.
//
// Usage:
//   source secrets/.env   # sets ASC_KEY_ID / ASC_ISSUER_ID / ASC_KEY_PATH
//   ASC_TOKEN=$(swift scripts/mint-asc-token.swift)
//   curl -sf -H "Authorization: Bearer $ASC_TOKEN" "https://api.appstoreconnect.apple.com/v1/apps?limit=200"
//
// Required env (from secrets/.env, gitignored — see build-time-secret-injection):
//   ASC_KEY_ID     — the API key's Key ID (Users and Access → Integrations)
//   ASC_ISSUER_ID  — the Issuer ID (UUID, not your Team ID)
//   ASC_KEY_PATH   — path to the downloaded AuthKey_<ASC_KEY_ID>.p8
//
// Mint fresh per run; a job that outlives the token re-mints instead of
// extending `exp`. See ../SKILL.md "Mint the token" for the claims this
// token carries and why (source: Apple's *Generating tokens for API
// requests*, 2026-07).
//
import CryptoKit
import Foundation

let env = ProcessInfo.processInfo.environment
guard let keyID = env["ASC_KEY_ID"], let issuerID = env["ASC_ISSUER_ID"],
      let keyPath = env["ASC_KEY_PATH"] else {
    FileHandle.standardError.write(Data("Set ASC_KEY_ID / ASC_ISSUER_ID / ASC_KEY_PATH (source secrets/.env)\n".utf8))
    exit(1)
}

func b64url(_ data: Data) -> String {
    data.base64EncodedString()
        .replacingOccurrences(of: "+", with: "-")
        .replacingOccurrences(of: "/", with: "_")
        .replacingOccurrences(of: "=", with: "")
}

let now = Int(Date().timeIntervalSince1970)
let header = #"{"alg":"ES256","kid":"\#(keyID)","typ":"JWT"}"#
// Apple rejects exp > 20 min ahead; 10 min leaves slack for clock skew.
let payload = #"{"iss":"\#(issuerID)","iat":\#(now),"exp":\#(now + 600),"aud":"appstoreconnect-v1"}"#
let signingInput = b64url(Data(header.utf8)) + "." + b64url(Data(payload.utf8))

let pem = try String(contentsOfFile: keyPath, encoding: .utf8)
let key = try P256.Signing.PrivateKey(pemRepresentation: pem)
let signature = try key.signature(for: Data(signingInput.utf8))  // ECDSA + SHA-256 = ES256
print(signingInput + "." + b64url(signature.rawRepresentation))  // rawRepresentation = r‖s, the JWT wire format
