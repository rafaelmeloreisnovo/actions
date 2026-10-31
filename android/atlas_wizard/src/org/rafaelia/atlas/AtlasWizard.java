package org.rafaelia.atlas;

import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.content.ClipData;
import android.database.Cursor;
import android.net.Uri;
import android.provider.OpenableColumns;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.graphics.Color;
import android.content.ContentResolver;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.InputStream;
import java.io.OutputStream;
import java.security.MessageDigest;

/* Platform Activity, with directly invoked freestanding native C11 ELF.
   No in-app OAuth, PAT, third-party library or network access permission. */
public final class AtlasWizard extends Activity implements View.OnClickListener {
 private static final int PICK=301, SAVE=302, LIMIT=16;
 private static final long MAX_BYTES=8L*1024L*1024L;
 private final String[] names=new String[LIMIT];
 private final long[] sizes=new long[LIMIT];
 private final String[] sha=new String[LIMIT];
 private final String[] gaps=new String[LIMIT];
 private int count=0;
 private boolean ready=false;
 private TextView status;
 private Button choose,export;
 private native int nativePlan(int key,int revision,int scope,int gap,int attest);

 @Override public void onCreate(Bundle state){
  super.onCreate(state);
  try{System.loadLibrary("atlas_l0");ready=true;}catch(Throwable ignored){ready=false;}
  LinearLayout main=new LinearLayout(this);
  main.setOrientation(LinearLayout.VERTICAL);
  main.setPadding(28,30,28,30);main.setBackgroundColor(Color.rgb(248,250,252));
  TextView title=new TextView(this);
  title.setText("RAFAELIA Ω Atlas / Drive\nAndroid ARM32 + ARM64");
  title.setTextSize(23);title.setTextColor(Color.rgb(17,39,62));main.addView(title);
  TextView instruction=new TextView(this);
  instruction.setText("1. Escolha até 16 arquivos usando o seletor Android.\n2. Gere um índice de metadados e escolha onde salvá-lo.\nO Google Drive pode aparecer como provedor. Nenhuma senha ou conteúdo é enviado sem sua escolha.");
  instruction.setTextSize(15);instruction.setPadding(0,20,0,22);main.addView(instruction);
  choose=new Button(this);choose.setText("1 · SELECIONAR ARQUIVOS");choose.setOnClickListener(this);main.addView(choose);
  export=new Button(this);export.setText("2 · SALVAR ÍNDICE");export.setOnClickListener(this);export.setEnabled(false);main.addView(export);
  status=new TextView(this);status.setTextSize(14);status.setTextColor(Color.rgb(30,50,75));
  status.setPadding(0,24,0,0);main.addView(status);
  ScrollView scroll=new ScrollView(this);scroll.addView(main);setContentView(scroll);
  status.setText(ready?"ELF L0 carregado. Selecione fontes.":"BLOQUEADO: biblioteca ELF incompatível ou ausente.");
 }
 @Override public void onClick(View v){
  if(v==choose){
   Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);
   i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("*/*");
   i.putExtra(Intent.EXTRA_ALLOW_MULTIPLE,true);
   startActivityForResult(i,PICK);
  }else if(v==export&&ready&&count>0){
   Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);
   i.addCategory(Intent.CATEGORY_OPENABLE);
   i.setType("application/json");
   i.putExtra(Intent.EXTRA_TITLE,"rafaelia-atlas-index.json");
   startActivityForResult(i,SAVE);
  }
 }
 @Override protected void onActivityResult(int code,int result,Intent data){
  super.onActivityResult(code,result,data);
  if(result!=RESULT_OK||data==null){
   status.setText("Operação cancelada. Dados anteriores preservados.");return;
  }
  if(code==PICK){
   count=0;
   ClipData clip=data.getClipData();
   if(clip!=null){
    for(int i=0;i<clip.getItemCount()&&count<LIMIT;i++)add(clip.getItemAt(i).getUri());
   }else if(data.getData()!=null)add(data.getData());
   export.setEnabled(ready&&count>0);
   status.setText("Indexados "+count+" de "+LIMIT+" arquivos.\nArquivo > 8 MiB: TOKEN_VAZIO_TOO_LARGE.\nNenhuma gravação remota automática.");
  }else if(code==SAVE&&data.getData()!=null){
   if(!ready){status.setText("BLOQUEADO: ELF não carregado.");return;}
   try{
    JSONObject root=new JSONObject();
    root.put("schema","rafaelia.atlas.saf-index.v1");
    root.put("scope","USER_SELECTED_ONLY");root.put("claim_allowed",false);
    JSONArray items=new JSONArray();
    for(int i=0;i<count;i++){
     JSONObject v=new JSONObject();
     v.put("name",names[i]);v.put("size",sizes[i]);
     v.put("sha256",sha[i]==null?JSONObject.NULL:sha[i]);
     v.put("gap",gaps[i]);
     int key=names[i]==null?1:names[i].hashCode();
     if(key==0)key=1;
     v.put("native_l0_status",nativePlan(key,1,2,1,7));
     items.put(v);
    }
    root.put("records",items);
    byte[] bytes=root.toString(2).getBytes("UTF-8");
    OutputStream out=getContentResolver().openOutputStream(data.getData(),"w");
    if(out==null)throw new IllegalStateException("No output");
    try{out.write(bytes);out.flush();}finally{out.close();}
    status.setText("Índice gravado no destino escolhido: "+bytes.length+" bytes.\nReadback remoto: TOKEN_VAZIO, ainda não atestado.");
   }catch(Exception e){status.setText("FALHA: "+e.getClass().getSimpleName()+". Persistência não confirmada.");}
  }
 }
 private void add(Uri uri){
  if(uri==null||count>=LIMIT)return;
  ContentResolver resolver=getContentResolver();
  String name="unnamed",digest=null,gap="TOKEN_VAZIO_UNREAD";long size=-1;
  Cursor c=null;
  try{
   c=resolver.query(uri,new String[]{OpenableColumns.DISPLAY_NAME,OpenableColumns.SIZE},null,null,null);
   if(c!=null&&c.moveToFirst()){
    int n=c.getColumnIndex(OpenableColumns.DISPLAY_NAME);
    int s=c.getColumnIndex(OpenableColumns.SIZE);
    if(n>=0&&!c.isNull(n))name=c.getString(n);
    if(s>=0&&!c.isNull(s))size=c.getLong(s);
   }
  }catch(Exception ignored){gap="TOKEN_VAZIO_METADATA";}
  finally{if(c!=null)c.close();}
  if(size<=MAX_BYTES){
   InputStream in=null;
   try{
    in=resolver.openInputStream(uri);
    if(in==null)throw new IllegalStateException("No input");
    MessageDigest md=MessageDigest.getInstance("SHA-256");
    byte[] buf=new byte[8192];long read=0;int n;
    while((n=in.read(buf))!=-1){
     if(n==0)continue;
     read+=n;if(read>MAX_BYTES){gap="TOKEN_VAZIO_TOO_LARGE";break;}
     md.update(buf,0,n);
    }
    if(read<=MAX_BYTES){
     char[] alphabet="0123456789abcdef".toCharArray();
     StringBuilder hex=new StringBuilder(64);
     for(byte b:md.digest()){hex.append(alphabet[(b>>4)&15]);hex.append(alphabet[b&15]);}
     digest=hex.toString();gap="TOKEN_VAZIO_RIGHTS_UNATTESTED";size=read;
    }
   }catch(Exception ignored){gap="TOKEN_VAZIO_READ_FAILED";}
   finally{if(in!=null)try{in.close();}catch(Exception ignored){}}
  }else gap="TOKEN_VAZIO_TOO_LARGE";
  names[count]=name;sizes[count]=size;sha[count]=digest;gaps[count]=gap;count++;
 }
}
